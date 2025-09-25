import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please provide a name'],
  },
  firstName: {
    type: String,
    required: [true, 'Please provide a first name'],
  },
  lastName: {
    type: String,
    required: [true, 'Please provide a last name'],
  },
  email: {
    type: String,
    required: [true, 'Please provide an email'],
    unique: true,
  },
  password: {
    type: String,
    required: [true, 'Please provide a password'],
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  lastLogin: {
    type: Date,
    default: null,
  },
  isFirstLogin: {
    type: Boolean,
    default: true,
  },
  profileCompleted: {
    type: Boolean,
    default: false,
  }
});

// Use mongoose.models.User || mongoose.model('User', userSchema) pattern
const User = mongoose.models.User || mongoose.model('User', userSchema);

export default User; 