// CLOCK
setInterval(()=>{
  const now = new Date();
  document.getElementById("clock").innerText = now.toLocaleTimeString();
},1000);

// GRAPH
let tempData=[], gasData=[], labels=[];

const chart = new Chart(document.getElementById("chart"),{
  type:'line',
  data:{
    labels:labels,
    datasets:[
      {label:'Temp',data:tempData,borderColor:'cyan'},
      {label:'Gas',data:gasData,borderColor:'red'}
    ]
  }
});

// LIVE DATA
setInterval(()=>{
fetch('/live')
.then(res=>res.json())
.then(d=>{

    console.log("LIVE:", d);

    document.getElementById("temp").innerText=d.temp+" °C";
    document.getElementById("humidity").innerText=d.humidity+" %";
    document.getElementById("gas").innerText=d.gas;

    // STATUS
    let s=document.getElementById("statusText");
    if(d.status==2){
        s.innerText="DANGER";
        s.style.color="red";
    }
    else if(d.status==1){
        s.innerText="WARNING";
        s.style.color="orange";
    }
    else{
        s.innerText="SAFE";
        s.style.color="green";
    }

    // SHELF
    document.getElementById("shelfLife").innerText=d.shelf;

    // GRAPH UPDATE
    tempData.push(d.temp);
    gasData.push(d.gas);
    labels.push('');

    if(tempData.length>10){
        tempData.shift();
        gasData.shift();
        labels.shift();
    }

    chart.update();

});
},2000);