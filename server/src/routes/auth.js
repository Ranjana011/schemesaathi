import { Router } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import rateLimit from "express-rate-limit";
import User from "../models/User.js";
import { requireAuth } from "../middleware/auth.js";

const router = Router();

// Limit brute-force attempts on login/signup
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 30,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Too many attempts, please try again later." },
});

function signToken(user) {
  return jwt.sign({ sub: user._id.toString() }, process.env.JWT_SECRET, {
    expiresIn: "30d",
  });
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ── SIGN UP ──
router.post("/signup", authLimiter, async (req, res) => {
  try {
    const { name, email, password, preferredLanguage } = req.body || {};

    if (!name || !name.trim()) return res.status(400).json({ error: "Name is required" });
    if (!email || !isValidEmail(email)) return res.status(400).json({ error: "A valid email is required" });
    if (!password || password.length < 8)
      return res.status(400).json({ error: "Password must be at least 8 characters" });

    const existing = await User.findOne({ email: email.toLowerCase().trim() });
    if (existing) return res.status(409).json({ error: "An account with this email already exists" });

    const passwordHash = await bcrypt.hash(password, 12);
    const user = await User.create({
      name: name.trim(),
      email: email.toLowerCase().trim(),
      passwordHash,
      preferredLanguage: preferredLanguage || "English",
    });

    const token = signToken(user);
    res.status(201).json({ token, user: user.toSafeJSON() });
  } catch (e) {
    console.error("Signup error:", e);
    res.status(500).json({ error: "Something went wrong creating your account" });
  }
});

// ── LOG IN ──
router.post("/login", authLimiter, async (req, res) => {
  try {
    const { email, password } = req.body || {};
    if (!email || !password) return res.status(400).json({ error: "Email and password are required" });

    const user = await User.findOne({ email: email.toLowerCase().trim() });
    if (!user) return res.status(401).json({ error: "Invalid email or password" });

    const match = await bcrypt.compare(password, user.passwordHash);
    if (!match) return res.status(401).json({ error: "Invalid email or password" });

    const token = signToken(user);
    res.json({ token, user: user.toSafeJSON() });
  } catch (e) {
    console.error("Login error:", e);
    res.status(500).json({ error: "Something went wrong logging you in" });
  }
});

// ── CURRENT USER ──
router.get("/me", requireAuth, async (req, res) => {
  const user = await User.findById(req.userId);
  if (!user) return res.status(404).json({ error: "User not found" });
  res.json({ user: user.toSafeJSON() });
});

// ── UPDATE PROFILE (e.g. preferred language, name) ──
router.patch("/me", requireAuth, async (req, res) => {
  const { name, preferredLanguage } = req.body || {};
  const update = {};
  if (name && name.trim()) update.name = name.trim();
  if (preferredLanguage) update.preferredLanguage = preferredLanguage;

  const user = await User.findByIdAndUpdate(req.userId, update, { new: true });
  if (!user) return res.status(404).json({ error: "User not found" });
  res.json({ user: user.toSafeJSON() });
});

export default router;
