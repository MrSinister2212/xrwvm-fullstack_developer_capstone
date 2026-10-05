const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');

const app = express();
const port = 3030;

app.use(cors());
app.use(express.json());

const reviewsData = JSON.parse(fs.readFileSync('reviews.json', 'utf8'));
const dealershipsData = JSON.parse(fs.readFileSync('dealerships.json', 'utf8'));

mongoose.connect('mongodb://mongo_db:27017/', { dbName: 'dealershipsDB' });

const Reviews = require('./review');
const Dealerships = require('./dealership');

async function seedData() {
  await Reviews.deleteMany({});
  await Reviews.insertMany(reviewsData.reviews);
  await Dealerships.deleteMany({});
  await Dealerships.insertMany(dealershipsData.dealerships);
}

mongoose.connection.once('open', () => {
  seedData().catch(console.error);
});

app.get('/', (req, res) => {
  res.send('Welcome to the Mongoose API');
});

app.get('/fetchReviews', async (req, res) => {
  try {
    res.json(await Reviews.find());
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    res.json(await Reviews.find({ dealership: Number(req.params.id) }));
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

app.get('/fetchDealers', async (req, res) => {
  try {
    res.json(await Dealerships.find());
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const state = req.params.state;
    if (state.toLowerCase() === 'all') {
      return res.json(await Dealerships.find());
    }

    const documents = await Dealerships.find({
      $or: [
        { state: { $regex: new RegExp('^' + state + '$', 'i') } },
        { st: { $regex: new RegExp('^' + state + '$', 'i') } }
      ]
    });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships by state' });
  }
});

app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const documents = await Dealerships.find({ id: Number(req.params.id) });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealer' });
  }
});

app.post('/insert_review', async (req, res) => {
  try {
    const latest = await Reviews.findOne().sort({ id: -1 });
    const newId = latest ? latest.id + 1 : 1;

    const review = new Reviews({
      id: newId,
      name: req.body.name,
      dealership: Number(req.body.dealership),
      review: req.body.review,
      purchase: req.body.purchase,
      purchase_date: req.body.purchase_date,
      car_make: req.body.car_make,
      car_model: req.body.car_model,
      car_year: Number(req.body.car_year),
    });

    res.json(await review.save());
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
