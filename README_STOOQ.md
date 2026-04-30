# Stooq Notes

## How to obtain an apikey
On or about 2026-04-01 Stooq implemented an apikey for website access. You will need to email
Stooq at www@stooq.com. Your email should describe your project and its use of data. In
return, Stooq will provide instructions describing how to obtain an apikey. Add your apikey to 
the configuration file as shown in the README.md file.

Here is how I obtained an apikey.

1. Open https://stooq.com/q/d/?s=^dji&get_apikey
2. Enter the captcha code.
3. Copy the CSV download link at the bottom of the page - it will contain the <apikey> variable.
4. Append the <apikey> variable with its value to your requests, e.g.
   https://stooq.com/q/d/l/?s=^dji&d1=20260331&d2=20260331&i=d&apikey=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
5. Add the apikey to the qf.conf file as described in the README.md file.

Thanks to Stooq for allowing access to historical data.
