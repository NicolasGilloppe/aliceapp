const express = require('express');
const bodyParser = require('body-parser');
const { MongoClient } = require('mongodb');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
const cors = require('cors');

const app = express();
/* const port = 8443; */
const port = 3000;

app.use(cors());
/* app.use(cors({
    origin: ['https://alicebetting.com', 'http://alicebetting.com']
})); */

 
// Add these lines to store the Telegram bot token and chat ID
const TELEGRAM_BOT_TOKEN = '6924139427:AAFJumXvbcqCNekj7TtzqwOKqvNXLZz0s9A';
const TELEGRAM_CHAT_ID = '-4052345424';

// Middleware to parse request body
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());


// Mongo DB Connection
const uri = "mongodb+srv://nicolasgilloppe:s0S8eaYt0mIMdYE7@alicedb.eqrplwk.mongodb.net/?retryWrites=true&w=majority&appName=alicedb";
const client = new MongoClient(uri);

async function connectToDatabase() {
    try {
        await client.connect();
        console.log("Connected to MongoDB Atlas");
    } catch (err) {
        console.error(err);
    }
}

// Connect to MongoDB Atlas
connectToDatabase();

async function emailExists(email) {
    const db = client.db("UsersDb");
    const collection = db.collection("Emails");
    const existingEmail = await collection.findOne({ email: email });
    return !!existingEmail;
}

// Add this new route to check for existing email
app.post('/check-email', async (req, res) => {
    const { email } = req.body;
    try {
      const exists = await emailExists(email);
      res.json({ exists });
    } catch (error) {
      console.error("Error checking email:", error);
      res.status(500).json({ error: "Server error while checking email" });
    }
});

// Add a new route to send messages to Telegram
app.post('/send-telegram-message', async (req, res) => {
    const { email } = req.body;
    console.log('Received request to send Telegram message for email:', email);
    
    const message = `New Whitelist Signup: ${email}`;
    
    const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
    const data = {
      chat_id: TELEGRAM_CHAT_ID,
      text: message
    };
  
    try {
      console.log('Sending request to Telegram API:', url);
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      console.log('Telegram API response:', result);
      if (result.ok) {
        res.status(200).json({ success: true });
      } else {
        res.status(400).json({ success: false, error: result.description });
      }
    } catch (error) {
      console.error('Error sending message to Telegram:', error);
      res.status(500).json({ success: false, error: 'Failed to send Telegram message' });
    }
});

// Define a route to handle POST requests from the form
app.post('/submit-form', async (req, res) => {
    const formData = req.body;
    const db = client.db("UsersDb");
    const collection = db.collection("Emails");
  
    try {
      // Check if email already exists
      const emailAlreadyExists = await emailExists(formData.email);
      if (emailAlreadyExists) {
        return res.status(400).json({ error: 'Email already exists' });
      }
  
      // Get today's date
      const today = new Date();
      const formattedDate = `${today.getDate()}-${today.getMonth() + 1}-${today.getFullYear()}`;
  
      // Add the date to the form data
      formData.join_date = formattedDate;
  
      // Insert the form data into the collection
      await collection.insertOne(formData);
      console.log("Form data inserted into database:", formData);
      res.status(200).json({ message: 'Form data saved to database' });
    } catch (err) {
      console.error("Error saving data to database:", err);
      res.status(500).json({ error: 'Error saving data to database' });
    }
});

// Start the server
/* app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
}); */

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});