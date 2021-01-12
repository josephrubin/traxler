"use strict";

const urlParams = new URLSearchParams(window.location.search);
const storage = window.localStorage;
let continueOnwardUrlParam = urlParams.get('c');

if (continueOnwardUrlParam === '1') {
  let continueUrlStorage = storage.getItem('ref') || '/';
  let ticketUrlParam = urlParams.get('ticket');
  fetch('https://' + apiDomain + '/validate', {
    method: 'POST',
    //cache: 'no-cache',
    credentials: 'include',
    headers: {
      'X-Cas-Ticket': ticketUrlParam
    }
  })
  .then(res => {
      // Add share ref to disable the back button if we are going to the
      // student page, because back would take us to login.
      window.location.href = continueUrlStorage + "&ref=share";
    },
    er => {
      document.getElementById('msg').innerHTML = "Error logging in."
    }
  )
}
else {
  let continueUrlParam = urlParams.get('ref') || '/';
  storage.setItem('ref', continueUrlParam);
  window.location.href = 'https://fed.princeton.edu/cas/login?service=' + encodeURIComponent('https://' + websiteDomain + '/login.html?c=1')
}
