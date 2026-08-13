import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true, maxlength: 100 },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      index: true,
    },
    passwordHash: { type: String, required: true },
    preferredLanguage: { type: String, default: "English" },
  },
  { timestamps: true }
);

// Never expose the password hash when a user document is serialized
userSchema.methods.toSafeJSON = function () {
  return {
    id: this._id,
    name: this.name,
    email: this.email,
    preferredLanguage: this.preferredLanguage,
    createdAt: this.createdAt,
  };
};

export default mongoose.model("User", userSchema);
