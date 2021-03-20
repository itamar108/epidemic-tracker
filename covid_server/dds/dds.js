// REQUIRES
const express = require('express');
const circleToPolygon = require("circle-to-polygon");
const country = require('countryjs');
const fs = require('fs').promises;
const fsn = require('fs');
const got = require('got');
const querystring = require('querystring');
const {getRandomDate, getRandomInt, drawLines, drawCountryRisk} = require("./ddsUtils.js");


// MISC CONSTANTS
const app = express();
const port = 3030;
const covid19APIBaseUrl = "https://api.covid19api.com";
const countryTmpName = `covid19-data-country-TEMP.json`;
let countryCodes = [];
let countryData = {};

const MIN_POLYGON_EDGES=10;
const MAX_POLYGON_EDGES=40;
const MIN_POLYGON_RADIUS=100;
const MAX_POLYGON_RADIUS=1000;
const MAX_NEW_CASES_PER_COUNTRY = 5;
const MAX_NUM_OF_COUNTRIES_PICKED_FOR_NEW_CASES = 7;

const popularCountries = [
    "china",
    "italy",
    "germany",
    "united-kingdom",
    "greece",
    "turkey",
    "japan",
    "spain",
    "france",
    "brazil",
    "ireland",
    "belgium",
    "russia",
    "israel",
    "thailand",
    "canada",
    "peru",
    "croatia",
    "austria",
    "new-zealand",
    "bolivia"];



async function loadData(filepath, url, formatter) {
    let path = filepath;
    let data = null, body;
    if (fsn.existsSync(path)) {
        console.log("Reading data from file: " + filepath);
        return JSON.parse(await fs.readFile(path, 'utf8'));
    } else {
        console.log("Reading data from url: " + url);
        body = JSON.parse((await got.get(url)).body);
    }
    data = formatter? formatter(body) : body;
    await fs.writeFile(path, JSON.stringify(data, null, 2));
    return data;
}

function getCountryRiskPerDay(countryName, countryData) {
    let risks = [];
    let prevDay = null;
    const countryISO2Code = countryCodes[countryName].ISO2;
    let population = country.population(countryISO2Code);
    countryData.forEach(day => {
         prevDay = prevDay || day;
        let newCases = 0;
        if(prevDay !== day) {
            newCases = day.Active - prevDay.Active;
            newCases = newCases < 0? 0 : newCases;
        }
        let newCaseAvg = day.Active === 0? 0 : (newCases / day.Active) * 100;
        let sickPopulationRatioFactor = day.Confirmed === 0? 0 :((day.Active / day.Confirmed)*100);
        const r = (newCaseAvg * sickPopulationRatioFactor * 0.5);
        risks.push({x: day.Date, y: r});
    });
    return risks;
}

function getSegmentOptions(min, max) {
    const minPercent = 30;
    const maxPercent = 95;
    let length = getRandomInt(min, max);
    let segmentLength = parseInt(getRandomInt(minPercent, maxPercent) / 100 * length);
    let segmentStartIdx = getRandomInt(0, length - segmentLength + 1);
    return { length, segmentStartIdx, segmentLength }
}

function generateRoute(center) {
    let segmentOptions = getSegmentOptions(MIN_POLYGON_EDGES, MAX_POLYGON_EDGES);
    let radius = getRandomInt(MIN_POLYGON_RADIUS, MAX_POLYGON_RADIUS) * segmentOptions.length / 10;
    let polygon = circleToPolygon(center, radius, segmentOptions.length);
    let polyCoordinates = polygon.coordinates[0];
    let route = polyCoordinates.slice(segmentOptions.segmentStartIdx, segmentOptions.segmentStartIdx + segmentOptions.segmentLength);
    return {route, polygon: polyCoordinates, radius}
}

async function loadCountriesData(countries, fetchAllData) {
    let countryData = {};
    const urlQueryParams = fetchAllData? "" : "?" + querystring.stringify({from: "2021-01-01T00:00:00Z", to: "2021-01-02T00:00:00Z"});
    for (let countryName of countries) {
        countryData[countryName] = {};
        countryData[countryName].data = await loadData("./" + countryTmpName.replace("TEMP", countryName),
            covid19APIBaseUrl + "/country/" + countryName + urlQueryParams,
            data => {
                return data.map(day => {
                    day.Date = day.Date.split("T")[0];
                    return day;
                });
            });
    }
    return countryData;
}

function generateNewCovid19Cases(maxNewCasesPerCountry) {
    let countriesPicked = [];
    let popularCountriesClone = [...popularCountries];
    let numOfCountriesPicked = getRandomInt(0, Math.min(MAX_NUM_OF_COUNTRIES_PICKED_FOR_NEW_CASES,popularCountries.length));

    if(numOfCountriesPicked === 0)
        return {};

    for (let i = 0; i < numOfCountriesPicked; i++) {
        let idx = getRandomInt(0, popularCountriesClone.length - 1);
        countriesPicked.push(popularCountriesClone[idx]);
        popularCountriesClone.splice(idx, 1)
    }

    let countryNewCases = {};

    countriesPicked.forEach(c => {
        let numOfCases = getRandomInt(1, maxNewCasesPerCountry);
        countryNewCases[c] = {};
        countryNewCases[c].cases = [];
        for (let i = 0; i < numOfCases; i++) {
            let countryDaySample = countryData[c].data[0];
            let caseCenter = [parseFloat(countryDaySample.Lon), parseFloat(countryDaySample.Lat)];
            countryNewCases[c].cases.push( {
                caseCenter,
                fullRoute: generateRoute(caseCenter)
            });
        }
    });
    return countryNewCases;
}

async function init() {

    console.log("Server is loading, please wait ...");

    countryCodes = await loadData("./countryCodes.json", covid19APIBaseUrl+"/countries", data => {
        let countryCodesObj = {};
        data.forEach(c => { countryCodesObj[c.Slug] = c; });
        return countryCodesObj;
    });
    countryData = await loadCountriesData(popularCountries, true);


    app.listen(port, () => {
        console.log(`DSS Server is listening at http://localhost:${port}`)
    });
}


// ##########################################################
//                         APIs
// ##########################################################

app.get('/disease-data-source/covid19/cases/confirmed', (req, res) => {
    const countriesCases = generateNewCovid19Cases(MAX_NEW_CASES_PER_COUNTRY);
    if(Object.keys(countriesCases).length === 0) {
        return res.status(404).send([]);
    }
    let response = [];
    const countryNames = Object.keys(countriesCases);
    let fromDate = new Date();
    fromDate.setDate(fromDate.getDate() - 30);
    for(let countryName of countryNames) {
        for(let c of countriesCases[countryName].cases) {
            response.push({
                route: c.fullRoute.route.map(point => { return {lat: point[0], lon: point[1]} }),
                date: getRandomDate(fromDate).toISOString().split("T")[0],
                country: countryCodes[countryName].ISO2
            });
        }
    }
    res.status(200).send(response);
});

app.get('/disease-data-source/covid19/drawRisks/:countryName', (req, res) => {
    const countryName = req.params.countryName;
    if(!countryData[countryName])
        return res.status(404).send("Country not found");

    const countryInfo = countryData[countryName].data;
    const risks = getCountryRiskPerDay(countryName, countryInfo);
    drawCountryRisk(countryInfo, risks);
    res.status(200).send("THIS IS ONLY DEV API, DO NOT USE");
});

init();
