// Copy Bitcoin address to clipboard
const copyBtn = document.getElementById('copy-btn');
const bitcoinAddress = document.getElementById('bitcoin-address');

copyBtn.addEventListener('click', () => {
  bitcoinAddress.select();
  document.execCommand('copy');
});

// Countdown timer
let timerSeconds = 900;
const timerEl = document.getElementById('timer');

function countdown() {
  const minutes = Math.floor(timerSeconds / 60);
  let seconds = timerSeconds % 60;
  seconds = seconds < 10 ? '0' + seconds : seconds;
  timerEl.innerHTML = `${minutes}:${seconds}`;
  if (timerSeconds <= 0) {
    clearInterval(timer);
    timerEl.innerHTML = 'Time is up!';
  } else {
    timerSeconds--;
  }
}

const timer = setInterval(countdown, 1000);

