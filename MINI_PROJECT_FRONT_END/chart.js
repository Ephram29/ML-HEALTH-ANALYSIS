const ctx = document.getElementById('myChart').getContext('2d');
const glucose = document.getElementById('glucose').getContext('2d');
let const_data=[12, 19, 3, 5, 2, 3]
function get_data(raw){
    const_data=raw;

const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
        datasets: [{
            label: 'your weight',
            data: const_data,
            backgroundColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            
    
        }]
    },
    options: {
        
                responsive: true,
            }
        }
    
    );
    }

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
        
        );