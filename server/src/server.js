import "dotenv/config";
import express from "express";
import cors from "cors";
import mongoose from "mongoose";
import authRoutes from "./routes/auth.js";

const app = express();
const PORT = process.env.PORT || 4000;

if (!process.env.MONGODB_URI) {
  console.error("❌ MONGODB_URI is not set. Copy .env.example to .env and fill it in.");
  process.exit(1);
}
if (!process.env.JWT_SECRET) {
  console.error("❌ JWT_SECRET is not set. Copy .env.example to .env and fill it in.");
  process.exit(1);
}

const allowedOrigins = (process.env.CORS_ORIGIN || "").split(",").map((s) => s.trim()).filter(Boolean);
app.use(
  cors({
    origin: allowedOrigins.length ? allowedOrigins : true,
    credentials: true,
  })
);
app.use(express.json());

app.get("/api/health", (req, res) => res.json({ ok: true, service: "scheme-saathi-auth" }));
app.use("/api/auth", authRoutes);

mongoose
  .connect(process.env.MONGODB_URI)
  .then(() => {
    app.listen(PORT, () => {
      console.log("=======================================================");
      console.log("  🔐  SchemeSaathi Auth Server (Node + Express + MongoDB)");
      console.log("=======================================================");
      console.log(`  Endpoints ready:`);
      console.log(`    POST  /api/auth/signup`);
      console.log(`    POST  /api/auth/login`);
      console.log(`    GET   /api/auth/me`);
      console.log(`    PATCH /api/auth/me`);
      console.log("=======================================================");
      console.log(`  ▶  Listening on http://localhost:${PORT}`);
      console.log("=======================================================");
    });
  })
  .catch((err) => {
    console.error("❌ Failed to connect to MongoDB:", err.message);
    process.exit(1);
  });
