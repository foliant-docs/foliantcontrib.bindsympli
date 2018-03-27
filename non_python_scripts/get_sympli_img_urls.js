#!/usr/bin/node


// Parameters

const cacheDir = process.argv[2];
const sympliLogin = process.argv[3];
const sympliPassword = process.argv[4];

if(!cacheDir || !sympliLogin || !sympliPassword)
{
    console.log('Three parameters must be specified: cache directory, Sympli login, Sympli password');
    process.exit(1);
}


// Input and output files
const designUrlsFile = cacheDir + '/design_urls.txt';
const imgUrlsFile = cacheDir + '/img_urls.txt';


// Using 'fs'
const fs = require('fs');


// Cleanup
if(fs.existsSync(imgUrlsFile)) {
    fs.unlinkSync(imgUrlsFile);
}


// Getting URLs of design pages

let designUrls = [];

if(fs.existsSync(designUrlsFile)) {
    designUrls = fs.readFileSync(designUrlsFile).toString().split("\n");
}
else {
    console.log("Design URLs list file does not exist");
    process.exit(1);
}


// Login page settings
const loginPageUrl = 'https://app.sympli.io/login/';
const usernameSelector = '#email';
const passwordSelector = '#password';
const buttonSelector = '#login-form > div.layout-login__form-button > button.btn.btn-primary';


// Design page settings
const imgSelector = 'div.general-canvas.preview-canvas-wrapper > div > div.preview-canvas.zdisable-anti-aliasing > img.sprite';


// Using Puppeteer

const puppeteer = require('puppeteer');

(async() => {
    // Launching Chromium
    const browser = await puppeteer.launch({args: ['--no-sandbox', '--disable-setuid-sandbox']});
    const page = await browser.newPage();


    // Disabling download of images

    await page.setRequestInterception(true);

    page.on('request', request => {
        if (request.resourceType === 'image') {
            request.abort();
        }
        else {
            request.continue();
        }
    });

    try {
        // Opening the login page
        console.log('Logging in');
        await page.goto(loginPageUrl, {timeout: 0});


        // Filling the email field
        await page.click(usernameSelector);
        await page.keyboard.type(sympliLogin);


        // Filling the password field
        await page.click(passwordSelector);
        await page.keyboard.type(sympliPassword);


        // Clicking the submit button
        await page.click(buttonSelector);


        // Waiting for load
        await page.waitForNavigation({waitUntil: 'load'});
    } catch (err) {
        console.error(err);
        process.exit(1);
    }


    // Processing design pages

    let output = '';

    for(let i = 0; i < designUrls.length; i++) {
        if(designUrls[i] != '') {
            try {
                // Opening an empty page
                console.log('Opening an empty page');
                await page.goto('about:blank');

                // Opening a design page
                console.log("Opening the design page: '" + designUrls[i] + "'");
                await page.goto(designUrls[i], {timeout: 0});

                // Waiting for the necessary element 'img'
                await page.waitForSelector(imgSelector);


                // Getting the value of 'src' attribute

                let imgSrc = await page.evaluate((imgSelector) => {
                    return document.querySelector(imgSelector).src;
                }, imgSelector);


                // Writing the result to STDOUT
                console.log("    Image URL: '" + imgSrc + "'");


                // Updating output
                output += designUrls[i] + "\t" + imgSrc + "\n";
            } catch(err) {
                console.error(err);
                process.exit(1);
            }
        }
    }


    // Closing Chromium
    browser.close();


    // Output
    fs.writeFile(imgUrlsFile, output, () => {});
})();
