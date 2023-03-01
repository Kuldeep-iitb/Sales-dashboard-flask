const roundNum = document.querySelectorAll(".round-num");
const emptyNum = document.querySelectorAll(".ifEmptyNum");
const statuses = document.querySelectorAll(".status");
const statusBalls = document.querySelectorAll(".statusBall");
const empty = document.querySelectorAll(".ifEmpty");

for (let i = 0; i < statuses.length; i++) {
  const statusText = statuses[i].innerText;
  const statusBall = statusBalls[i];
  if (statusText == "customer") {
    statusBall.classList.add("text-success");
    statuses[i].innerText = "Customer";
  } else if (statusText == "inactive") {
    statusBall.classList.add("text-warning");
    statuses[i].innerText = "Inactive";
  } else if (statusText == "prospect") {
    statusBall.classList.add("text-info");
    statuses[i].innerText = "Prospect";
  }
  else if (statusText == "not interested") {
    statusBall.classList.add("text-danger");
    statuses[i].innerText = "Not interested"
  }
}
for (let i = 0; i < empty.length; i++) {
  const emptyText = empty[i].innerText;
  if (emptyText == "") {
    empty[i].innerText = "N/A";
  }
}

roundNum.forEach((num) => {
  if (num.innerText.length > 6) {
    num.innerText = (num.innerText / 1000000).toFixed(1) + "Mkr";
  } else if (num.innerText.length > 3) {
    num.innerText = (num.innerText / 1000).toFixed(0) + "kkr";
  }
});

emptyNum.forEach((num) => {
  if (num.innerText == "") {
    num.innerText = "0kr";
  }
});