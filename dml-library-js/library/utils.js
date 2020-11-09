"use strict";
exports.__esModule = true;


/**
 * Make the HTTP URL for the server.
 * 
 * @param {string} repoID The repo ID associated with the dataset. 
 */
function makeHTTPURL(repoID) {
    return `http://${repoID}.cloud.discreetai.com`
}

/**
 * Make the WebSocket URL for the server.
 * 
 * @param {string} repoID The repo ID associated with the dataset. 
 */
function makeWSURL(repoID) {
    return `ws://${repoID}.cloud.discreetai.com`;
}

exports.makeHTTPURL = makeHTTPURL;
exports.makeWSURL = makeWSURL;