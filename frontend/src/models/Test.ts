import mongoose from 'mongoose';

const testSchema = new mongoose.Schema({
  name: String
}, { 
  collection: 'users' // Using just 'users' as the collection name
});

// Force Mongoose to use a new model instance
try {
  mongoose.deleteModel('Test'); // Clear any existing model
} catch {
  // Model doesn't exist yet, which is fine
}
const Test = mongoose.model('Test', testSchema);

export default Test; 