const { plot } = require('nodeplotlib');

function getRandomDate(from) {
    from = from.getTime();
    to = new Date();
    return new Date(from + Math.random() * (to - from));
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function drawCountryRisk(countryData, riskData) {
    let x=[], y=[];
    let riskX=[], riskY=[];
    countryData.forEach(day => {
        x.push(day.Date);
        y.push(day.Active);
    });
    console.log("risks:" + JSON.stringify(riskData));
    riskData.forEach(r => {
        riskX.push(r.x);
        riskY.push(r.y);
    });

    console.log("risks:" + JSON.stringify(riskData));
    drawLines({x,y}, {x: riskX, y: riskY} );
}

function drawLines(...xys) { // [ {x: [ all x's], y: [ all y's]}, ...]
    let data = [];
    console.log("ALL XYS" + JSON.stringify(xys));
    for(let xy of xys) {
        data.push({ x: xy.x, y: xy.y, type: 'line' });
    }
    plot(data);
}


function getRandomPointOnGeoCircle(centerX, centerY, radius) {
    var angle = Math.random()*Math.PI*2;
    const x = Math.cos(angle)*radius;
    const y = Math.sin(angle)*radius;
    return [centerX + x, centerY + y];
}

function transformRouteCoordinates(coordinates) {
    let x = [], y = [];
    coordinates.forEach(c => {
        x.push(c[0]);
        y.push(c[1]);
    });
    return {x, y};
}


exports.getRandomDate = getRandomDate;
exports.getRandomInt = getRandomInt;
exports.drawLines = drawLines;
exports.drawCountryRisk = drawCountryRisk;