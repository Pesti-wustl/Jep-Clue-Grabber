const express = require('express')
const app = express()
app.use(express.json())
const { Pool } = require('pg')

//environment variables
const path = require('path')
require('dotenv').config({path: path.resolve(__dirname, './.env')})

const cors = require('cors')
app.use(cors())

const fs = require('fs')

const pool = new Pool({
    connectionString: process.env.SUPABASE_CONNECTION_STRING
})

const checkCategoryAndGetId = async (categoryName, gameId, gameYear) => {
    const sql = 'SELECT id FROM categories WHERE category_name = $1 AND game_id = $2 AND game_year = $3'
    const values = [categoryName, gameId, gameYear]
    const result = await pool.query(sql, values)
    return result.rows.length > 0 ? result.rows[0].id : null
}

const insertCategoryAndGetId = async (categoryName, gameId, gameYear, categoryOrder) => {
    const insertSql = 'INSERT INTO categories (cat_category_name, game_id, game_year, category_order) VALUES ($1, $2, $3, $4) RETURNING id'
    const insertValues = [categoryName, gameId, gameYear, categoryOrder]
    const insertResult = await pool.query(insertSql, insertValues)
    return insertResult.rows[0].id
}


const addCluesToPostgres = async (clues) => {
    try {
        for (const clue of clues) {
            if (clue.clue_value === 'ERROR') {
                throw new Error("Invalid clue");
            }

            const isDuplicate = await checkIfDuplicate(clue)
            if (isDuplicate) {
                return null;
            }

            let categoryId = await checkCategoryAndGetId(clue.clue_category, clue.clue_game_id, clue.game_year);
            if (categoryId === null) {
                categoryId = await insertCategoryAndGetId(clue.clue_category, clue.clue_game_id, clue.game_year, clue.category_order);
            }

            const sql = 'INSERT INTO jeopardy_clues (game_id, game_year, clue_value, clue_order, category_id, clue_round, clue_question, clue_answer, category_name) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)';
            const values = [clue.clue_game_id, clue.game_year, clue.clue_value, clue.clue_order, categoryId, clue.clue_round, clue.clue_question, clue.clue_answer, clue.clue_category];

            await pool.query(sql, values);
        }
        console.log("A batch of clues have been added");
    } catch (error) {
        console.log("CAUGHT ERROR", error);
        throw error;
    }
};


const checkIfDuplicate = async (clue) => {

    try {
        const sql = 'SELECT COUNT(*) FROM jeopardy_clues WHERE game_id = $1 AND clue_question = $2 AND clue_answer = $3'
        const values = [clue.clue_game_id, clue.clue_question, clue.clue_answer]

        const result = await pool.query(sql, values)

        return result.rows[0].count > 0
    } catch (err) {
        console.log("Error in checkIfDuplicate", err.message)
        return false
    }
}

const getRandomClue = async () => {
    try {
        const countResult = await pool.query('SELECT COUNT(*) FROM jeopardy_clues')
        const count = parseInt(countResult.rows[0].count)
        const randomindex = Math.floor(Math.random() * count)

        const sql = 'SELECT * FROM jeopardy_clues OFFSET $1 LIMIT 1'
        const result = await pool.query(sql, [randomindex])
        console.log(result.rows[0])
        return result.rows[0]
    } catch (error) {
        console.log("Error in getRandomClue", error.message)
        throw error
    }
}

app.post("/jepClues", async (request, response) => {
    try {
        await addCluesToPostgres([...request.body])
        response.send("Success")
    } catch (error) {
        response.status(400).send(error.message)
    }
})

app.get("/", (request, response) => {
    const filePath = path.join(__dirname, "./info_htmls/info.html")
    fs.readFile(filePath, 'utf8', function(err, data) {
        response.send(data)
    })
})
app.get("/random", async (request, response) => {
    try {
        const result = await getRandomClue()
        response.json(result)
    } catch (error) {
        console.log("Error in /random", error.message)
        response.status(500).send("Error fetching random clue")
    }
})

// not too worried about this right now, edit later. 
app.get("/randomGame/:gameId", async (request, response) => {
    let game_id = request.params['gameId']
    const categories = await Clue.aggregate([
        {$match : {clue_game_id: game_id}},
        {$group : {_id: {clue_round: '$clue_round', clue_category : '$clue_category'}, clues: {$push: '$$ROOT'}}},
        {$match : {'_id.clue_round': {$in : ['single_jeopardy', 'double_jeopardy', 'final_jeopardy'] }}},
        {$project: {_info: '$_id', clues: 1, _id: 0}},
        {$sort : {'_id.clue_round': 1}}
    ]).exec()
    response.json(categories)
})

process.on('SIGINT', async () => {
    console.log("Shutting down...")

    try {
        await pool.end()
        console.log("Postgres connection closed")
    } catch (error) {
        console.log("Error closing Postgres connection")
    }

    console.log("Express server closed")
    process.exit(0)
})

const PORT = process.env.port || 8080
app.listen(PORT, () => {
    console.log(`Listening on PORT:${PORT}`)
})



