import express from "express";
import cors from 'cors';
import http from 'http';
import fs from 'fs';

const app = express();
app.use(cors());

// summary.json全体
app.get('/summary', async (req, res) => {
    const data = JSON.parse(await fs.readFileSync('/data/summary.json', 'utf8'));
    res.json(data.data);
});

// 最新のリザルトIDを取得したいとき
app.get('/summary/lastid', async (req, res) => {
    const data = JSON.parse(await fs.readFileSync('/data/summary.json', 'utf8'));
    res.json(data.data.coopResult.historyGroupsOnlyFirst.nodes[0].historyDetails.nodes[0]);
});

// リザルト一つずつを取得する
app.get('/result/:id', async (req, res) => {
    try {
        const filePath = '/data/results/' + req.params.id + '.json';
        fs.statSync(filePath);
        // const fileState = fs.statSync(filePath);
        // console.log(fileState)
        const data = JSON.parse(await fs.readFileSync(filePath, 'utf8'));
        res.json(data.data);
    }
    catch (err) {
        // console.log(err);
        res.status(404).json({ msg: { error: "file not found." } });
    }
});

const webServer = http.createServer(app);
webServer.listen(3000, () => {
    console.log("server running PORT:" + 3000);
});
