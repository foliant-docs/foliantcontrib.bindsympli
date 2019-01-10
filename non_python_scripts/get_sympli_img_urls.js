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
    // Launching Chrome
    const browser = await puppeteer.launch({args: ['--no-sandbox', '--disable-setuid-sandbox']});
    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(60000);

    try {
        // Opening the login page
        console.log('Opening the login page');
        await page.goto(loginPageUrl, {waitUntil: 'networkidle2'});


        // Filling the email field
        console.log('Filling the email field');
        await page.focus(usernameSelector, {delay: 500});
        await page.keyboard.type(sympliLogin);


        // Filling the password field
        console.log('Filling the password field');
        await page.focus(passwordSelector, {delay: 500});
        await page.keyboard.type(sympliPassword);


        // Clicking the submit button
        console.log('Clicking the submit button');
        await page.click(buttonSelector);


        // Waiting for an after-login page load
        console.log('Waiting for an after-login page load');
        await page.waitForNavigation({waitUntil: 'networkidle2'});
    } catch (err) {
        console.error(err);
        process.exit(1);
    }


    // Disable images downloading

    await page.setRequestInterception(true);

    page.on('request', interceptedRequest => {
        if (interceptedRequest.resourceType() === 'image') {
            interceptedRequest.abort();
        }
        else {
            interceptedRequest.continue();
        }
    });


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
                await page.goto(designUrls[i], {waitUntil: 'networkidle2'});
                let title = await page.title();


                // Checking if the design page found

                if(title != 'Not Found - Sympli')
                {
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
                }
                else
                {
                    // Writing the result to STDOUT
                    console.log("    Design not found");


                    // Updating output
                    output += designUrls[i] + "\t" + 'NOT_FOUND' + "\n";
                }
            } catch (err) {
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
