const express = require('express')
const app = express()
app.use(express.json())

//environment variables
const path = require('path')
require('dotenv').config({path: path.resolve(__dirname, '../.env')})

const cors = require('cors')
app.use(cors())

const mongoose = require('mongoose')
const url = `mongodb+srv://${process.env.MONGODB_USERNAME}:${process.env.MONGODB_PASSWORD}@cluster0.jkch2xx.mongodb.net/?retryWrites=true&w=majority`
//
const addCluesToMongoDB = async (clues) => {
    try {
        //Add all clues and then promise not to end until they are all added
        const cluePromises = clues.map(async (clue) => {
            const newClue = new Clue({
                clue_game_id: clue.clue_game_id || 'ERROR',
                game_year: clue.game_year || 'ERROR',
                clue_value: clue.clue_value || 'ERROR',
                clue_category: clue.clue_category || 'ERROR',
                clue_round: clue.clue_round || 'ERROR',
                clue_question: clue.clue_question || 'ERROR',
                clue_answer: clue.clue_answer || 'ERROR'
            })
            
            console.log(newClue)
            if (newClue.clue_value == 'ERROR') {
                console.log("ERROR!!!!!!")
                throw new Error("Invalid clue")
            }
            
            const alreadyinMongoDB = await checkIfDuplicate(newClue)
            if (alreadyinMongoDB) {
                console.log("Duplicate clue... Skipping")
                return null;
            }
            return newClue.save()
        })
    
        await Promise.all(cluePromises) //Ensures the mapping finishes before closing the connection
        
        console.log("A batch of clues have been added")

    } catch (error) {
        console.log("CAUGHT ERROR")
        throw error
    }
}

const checkIfDuplicate = async (clue) => {

    try {
        const result = await Clue.find({clue_game_id: clue.clue_game_id, clue_question: clue.clue_question});
        return result.length > 0
    } catch (err) {
        console.log(err)
        return false
    }
}

const getRandomClue = async () => {
    return new Promise((resolve, reject) => {
        Clue.countDocuments().exec()
            .then(count => {
                const random = Math.floor(Math.random() * count)
                return Clue.findOne().skip(random).exec()
            })
            .then(result => {
                resolve(result)
            })
            .catch(error => {
                reject(error)
            })
    })
}

mongoose.set('strictQuery', false)
mongoose.connect(url)

const clueSchema = new mongoose.Schema({
    clue_game_id: String,
    game_year: String,
    clue_value: String,
    clue_category: String,
    clue_round: String,
    clue_question: String,
    clue_answer: String
})

const Clue = mongoose.model('Clue', clueSchema)

app.put("/jepClues", async (request, response) => {
    try {
        await addCluesToMongoDB([...request.body])
        response.send("Success")
    } catch (error) {
        response.status(400).send(error.message)
    }
})

app.get("/random", (request, response) => {
    getRandomClue()
        .then(result => {
            response.json(result)
        })
})

process.on('SIGINT', () => {
    console.log("goodbye!")
    mongoose.connection.close()
    server.close(() => {
        console.log("we're done")
        process.exit(0)
    })
})

const PORT = 8080
const server = app.listen(PORT, () => {
    console.log(`Listening on PORT:${PORT}`)
})



