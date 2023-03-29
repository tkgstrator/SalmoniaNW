/* global Vue axios */
Vue.createApp({
    setup() {
        // 設定系項目
        // | axiosのbaseURL
        axios.defaults.baseURL = "http://localhost:3000/";
        // | 勝敗リストで表示する数（直近何回分か）
        const statsNumber = 10;
        // | シフト終了後どれくらいの分数結果を保持するか
        const shiftPadding = 7;

        // ポーリングのタイマー
        let timer;

        // 評価
        const gradeName = Vue.ref('');
        const gradePoint = Vue.ref(40);

        // うろこの数
        const scale = Vue.ref({ gold: 0, silver: 0, bronze: 0 });

        // クマサンポイントカードの情報
        const pointCard = Vue.ref({
            "defeatBossCount": 0,
            "deliverCount": 0,
            "goldenDeliverCount": 0,
            "playCount": 0,
            "rescueCount": 0,
            "regularPoint": 0,
            "totalPoint": 0
        });

        // 作業上必要な物
        // | 一番新しい記録（summary.jsonより取得）
        const latestId = Vue.ref('');
        // | 直近の記録のシフトの開始・終了時間（summary.jsonより取得）
        const latestShiftStarts = Vue.ref('');
        const latestShiftEnds = Vue.ref('');
        // | 表示に際してフォーマットしたシフトの時間を返す
        // const dateLatestShiftStarts = Vue.computed(() => {
        //     moment.locale('ja');
        //     return moment(latestShiftStarts.value).format('llll');
        // });
        // | イニシャライズフラグ
        const init = Vue.ref(false);
        // | 最新データが読み込まれたかどうかチェックフラグ
        const latestReadId = Vue.ref('');
        // | getAllResultが完了済みかどうかのフラグ
        const getAllFlag = Vue.ref(true);

        // シフト内の記録を全部保管する配列
        const resultsAll = Vue.ref([]);

        // シフト内のプレイ回数
        const shiftPlayCount = Vue.ref(0);
        // シフト内の勝利数
        const shiftWinCount = Vue.ref(0);
        // シフト内の敗北数（プレイ回数と勝利数の差分）
        const shiftDefeatCount = Vue.computed(() => {
            return shiftPlayCount.value - shiftWinCount.value;
        });
        // 勝敗リスト（勝ち星表示用）
        const shiftStatsList = Vue.ref([]);
        const shiftStatsListSliced = Vue.computed(() => {
            return shiftStatsList.value.slice(0, statsNumber - 1);
        })

        // オオモノの数の配列
        // | バクダン
        const countSteelhead = Vue.ref([]);
        // | カタパッド
        const countFlyfish = Vue.ref([]);
        // | テッパン
        const countScrapper = Vue.ref([]);
        // | ヘビ
        const countSteelEel = Vue.ref([]);
        // | タワー
        const countStinger = Vue.ref([]);
        // | モグラ
        const countMaws = Vue.ref([]);
        // | コウモリ
        const countDrizzler = Vue.ref([]);
        // | ハシラ
        const countFishStick = Vue.ref([]);
        // | ダイバー
        const countFlipperFlopper = Vue.ref([]);
        // | テッキュウ
        const countBigShot = Vue.ref([]);
        // | ナベブタ
        const countSlamminLid = Vue.ref([]);


        // オオモノの数の計算結果
        // | バクダン
        const countSteelheadDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countSteelhead.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | カタパッド
        const countFlyfishDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countFlyfish.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | テッパン
        const countScrapperDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countScrapper.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | ヘビ
        const countSteelEelDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countSteelEel.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | タワー
        const countStingerDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countStinger.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | モグラ
        const countMawsDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countMaws.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | コウモリ
        const countDrizzlerDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countDrizzler.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | ハシラ
        const countFishStickDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countFishStick.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | ハシラ
        const countFlipperFlopperDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countFlipperFlopper.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | ナベブタ
        const countBigShotDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countBigShot.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });
        // | ナベブタ
        const countSlamminLidDefeat = Vue.computed(() => {
            let count = {
                defeatCount: 0,
                teamDefeatCount: 0,
                popCount: 0
            };
            countSlamminLid.value.forEach(function (game) {
                count.defeatCount += game.defeatCount;
                count.teamDefeatCount += game.teamDefeatCount;
                count.popCount += game.popCount;
            });
            return count;
        });

        // 直近の出現数
        const latestBossCount = Vue.computed(() => {
            let count = {
                steelhead: 0,
                flyfish: 0,
                scrapper: 0,
                steeleel: 0,
                stinger: 0,
                maws: 0,
                drizzler: 0,
                fishstick: 0,
                flipperflopper: 0,
                bigshot: 0,
                slamminlid: 0,
            }

            if (countSteelhead.value.length > 0) {
                count.steelhead = getPopCount(countSteelhead);
                count.flyfish = getPopCount(countFlyfish);
                count.scrapper = getPopCount(countScrapper);
                count.steeleel = getPopCount(countSteelEel);
                count.stinger = getPopCount(countStinger);
                count.maws = getPopCount(countMaws);
                count.drizzler = getPopCount(countDrizzler);
                count.fishstick = getPopCount(countFishStick);
                count.flipperflopper = getPopCount(countFlipperFlopper);
                count.bigshot = getPopCount(countBigShot);
                count.slamminlid = getPopCount(countSlamminLid);
            }
            return count;
        });

        // 直近のキケン度（%）
        const latestDangerRate = Vue.ref('N/A');

        // ************* methods *************
        // 待機用の関数
        const _sleep = (ms) => {
            new Promise((resolve) => {
                setTimeout(resolve, ms);
            })
        }

        // summary.jsonを読み込む
        const getSummary = async function () {
            console.groupCollapsed('summaryを読み込むよ！');
            let response;
            // ここから新
            try {
                response = await axios.get('/summary');
                console.log('summary取得成功');
            } catch (error) {
                console.error(error);
            }
            // 直近でプレイしたシフトの時刻
            latestShiftStarts.value = response.data.coopResult.historyGroups.nodes[0].startTime;
            latestShiftEnds.value = response.data.coopResult.historyGroups.nodes[0].endTime;
            // 評価の称号は無条件に拾う
            gradeName.value = response.data.coopResult.regularGrade.name;
            // 評価の数値は一旦40に
            // gradePoint.value = 40;
            // うろこ部分
            scale.value = response.data.coopResult.scale;
            // ポイントカードの情報
            pointCard.value = response.data.coopResult.pointCard;
            // 直近のリザルトID
            const latest = response.data.coopResult.historyGroupsOnlyFirst.nodes[0].historyDetails.nodes[0].id;

            // 今よりもシフト終了時刻が前だったら値を上書き
            const endTime = new Date(latestShiftEnds.value);
            const now = new Date();
            endTime.setMinutes(endTime.getMinutes() + shiftPadding);
            if (endTime > now) {
                // 評価の数値を上書き
                gradePoint.value = response.data.coopResult.regularGradePoint;
            }
            // イニシャライズのフラグをtrueに
            init.value = true;
            if (latest !== latestId.value || shiftPlayCount.value === 0) {
                latestId.value = latest;
                await _sleep(2000); // Python側の処理対策で1秒待つ
                getAllResults();
            }
            console.groupEnd();
        };

        // リザルトのjsonを読み込む
        const getResult = async function (resultId) {
            console.groupCollapsed(`ID: ${resultId} のデータを読み込むよ！`);

            let value;
            let response;
            // ここから新
            try {
                response = await axios.get('/result/' + resultId);
                console.log('リザルト取得成功');


                const tmp = response.data;

                if (!tmp.coopHistoryDetail) {
                    return;
                }

                const playedTime = new Date(tmp.coopHistoryDetail.playedTime);
                const shiftStarts = new Date(latestShiftStarts.value);
                const shiftEnds = new Date(latestShiftEnds.value);
                const now = new Date();
                shiftEnds.setMinutes(shiftEnds.getMinutes() + shiftPadding);

                if (playedTime > shiftStarts && now < shiftEnds) {
                    resultsAll.value.push(tmp);
                    console.log('リザルトを追加したよ！');
                    // プレイ回数を加算
                    shiftPlayCount.value++;
                    // 勝利数を加算
                    if (tmp.coopHistoryDetail.resultWave === 0) {
                        shiftWinCount.value++;
                    }
                    // 勝敗リストに追加
                    shiftStatsList.value.push(tmp.coopHistoryDetail.resultWave);
                    shiftStatsList.value.splice();
                    // オオモノ情報の追加
                    getEnemyCount(tmp.coopHistoryDetail.enemyResults);

                    value = tmp.coopHistoryDetail.previousHistoryDetail.id;

                    if (resultId === latestId.value) {
                        // キケン度更新
                        latestDangerRate.value = Math.round(tmp.coopHistoryDetail.dangerRate * 1000) / 10;
                    }
                } else {
                    console.log('直近のシフトのデータじゃないので無視したよ！');
                    value = false;
                }

            }
            catch (error) {
                console.error(error);
                // 200以外なら抜ける
                if (error.response.status == 200) {
                    _sleep(1000);
                } else {
                    value = false;
                }
            }

            console.groupEnd();
            return value;
        };


        // 直近のシフトのリザルトを一式読み込む
        const getAllResults = async function () {
            console.group('getAllResults');
            if (latestReadId.value !== latestId.value) {
                getAllFlag.value = false;
                let flag = true;
                let id = latestId.value;

                let res = '';

                shiftPlayCount.value = 0;
                shiftWinCount.value = 0;
                shiftStatsList.value = [];
                shiftStatsList.value.splice();

                //オオモノの数のリセット
                countSteelhead.value.length = 0;
                countSteelhead.value.splice();
                countFlyfish.value.length = 0;
                countFlyfish.value.splice();
                countScrapper.value.length = 0;
                countScrapper.value.splice();
                countSteelEel.value.length = 0;
                countSteelEel.value.splice();
                countStinger.value.length = 0;
                countStinger.value.splice();
                countMaws.value.length = 0;
                countMaws.value.splice();
                countDrizzler.value.length = 0;
                countDrizzler.value.splice();
                countFishStick.value.length = 0;
                countFishStick.value.splice();
                countFlipperFlopper.value.length = 0;
                countFlipperFlopper.value.splice();
                countBigShot.value.length = 0;
                countBigShot.value.splice();
                countSlamminLid.value.length = 0;
                countSlamminLid.value.splice();

                // 前のidが返ってきたらそのidのjsonを取りに行く
                // falseが返ってきたらそこで終了
                while (flag) {
                    await getResult(id).then(resId => {
                        res = resId;
                        if (id === latestId.value) {
                            latestReadId.value = id;
                        }
                    });
                    if (res === false) {
                        flag = false;
                    } else {
                        id = res;
                    }
                }

                getAllFlag.value = true;
            } else {
                console.log('最新情報は取得済みだったよ！');
            }
            console.groupEnd();
        }

        // 各オオモノのデータをまとめる
        const getEnemyCount = function (res) {
            res.forEach(function (data) {
                // バクダン
                if (data.enemy.id === 'Q29vcEVuZW15LTQ=') {
                    countSteelhead.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // カタパッド
                else if (data.enemy.id === 'Q29vcEVuZW15LTU=') {
                    countFlyfish.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // テッパン
                else if (data.enemy.id === 'Q29vcEVuZW15LTY=') {
                    countScrapper.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // ヘビ
                else if (data.enemy.id === 'Q29vcEVuZW15LTc=') {
                    countSteelEel.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // タワー
                else if (data.enemy.id === 'Q29vcEVuZW15LTg=') {
                    countStinger.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // モグラ
                else if (data.enemy.id === 'Q29vcEVuZW15LTk=') {
                    countMaws.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // コウモリ
                else if (data.enemy.id === 'Q29vcEVuZW15LTEw') {
                    countDrizzler.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // ハシラ
                else if (data.enemy.id === 'Q29vcEVuZW15LTEx') {
                    countFishStick.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // ダイバー
                else if (data.enemy.id === 'Q29vcEVuZW15LTEy') {
                    countFlipperFlopper.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // テッキュウ
                else if (data.enemy.id === 'Q29vcEVuZW15LTEz') {
                    countBigShot.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
                // ナベブタ
                else if (data.enemy.id === 'Q29vcEVuZW15LTE0') {
                    countSlamminLid.value.push({
                        defeatCount: data.defeatCount,
                        teamDefeatCount: data.teamDefeatCount,
                        popCount: data.popCount,
                    });
                }
            });
        }

        // 0番目のpopCountを返すヤツ
        const getPopCount = function (obj) {
            if (obj.value[0].popCount) {
                return obj.value[0].popCount;
            } else {
                return 0;
            }
        }

        // ポーリング用
        const polling = async function () {
            console.group('polling start');
            await getSummary();
            console.groupEnd('polling end');
        }

        Vue.onMounted(async () => {
            await getSummary();
            // const tmpShiftEnds = new Date(latestShiftEnds.value);
            // if (tmpShiftEnds.setMinutes(tmpShiftEnds.getMinutes() + shiftPadding) > Date()) {
            // if (latestReadFlag.value === false) {
            //     await getAllResults();
            // }
            // } else {
            // gradePoint.value = 40;
            // }
            timer = window.setInterval(polling, 5000);
        });

        Vue.watch(latestId.value, async () => {
            if (init.value) {
                await getAllResults();
            }
        });

        Vue.onBeforeUnmount(() => {
            window.clearInterval(timer);
        })

        return {
            gradeName,
            gradePoint,
            scale,
            pointCard,
            shiftPlayCount,
            shiftWinCount,
            shiftDefeatCount,
            shiftStatsList,
            shiftStatsListSliced,
            latestDangerRate,
            countSteelheadDefeat,
            countFlyfishDefeat,
            countScrapperDefeat,
            countSteelEelDefeat,
            countStingerDefeat,
            countMawsDefeat,
            countDrizzlerDefeat,
            countFishStickDefeat,
            countFlipperFlopperDefeat,
            countBigShotDefeat,
            countSlamminLidDefeat,
            latestBossCount
        };
    },
}).mount('#app');
