const ctx = document.getElementById('myChart').getContext('2d');
//const glucose = document.getElementById('glucose').getContext('2d');
let const_data=[12, 19, 3, 5, 2, 3]
function get_data(raw){
    const_data=raw;
    colors=[]
    
    var gradient = ctx.createLinearGradient(0, 0, 0, 90);
    gradient.addColorStop(0, 'rgba(247,215,3,1)');
    gradient.addColorStop(1, 'rgba(254,156,0,1)');
    for (i = 0; i < const_data.length; i++) {
        colors[i] =gradient;

    }
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['18/1/22', '19/2/22', '20/3/22', '18/4/22', '5/7/22', '16/7/22'],
        datasets: [{
            label: 'your weight',
            minBarLength: 8,
            data: const_data,
            backgroundColor: colors,
            
    
        }]
    },
    options: {
        maintainAspectRatio: false,
                responsive: true,
            }
        }
    
    );
    }
/*
    const myglucose = new Chart(glucose, {
        type: 'line',
        data: {
            labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
            datasets: [{
                label: 'your glucose level',
                data: const_data,
                backgroundColor:  'rgba(207, 0, 15, 0.1)',
                borderColor:'rgba(207, 0, 15, 1)',
                fill:true,
                tension:0.4
        
            }]
        },
        options: {
            
                    responsive: true,
                }
            }
        
        );*/