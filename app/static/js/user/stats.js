const renderChart = (data, labels) => {
    var ctx = document.getElementById('mychart').getContext("2d");

    const xValues = [100,200,300,400,500,600,700,800,900,1000];

    new Chart(ctx, {
    type: "doughnut",
    data: {
        labels: labels,
        datasets: [{
        label: "Last 6 months expenses",
        data: data,
        backgroundColor: [    
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)',
            'rgb(255, 29, 142)',
            'rgb(0, 122, 35)',
            'rgb(25, 05, 86)',
            'rgb(0, 9, 82)',
            'rgb(4, 162, 23)',
            'rgb(255, 25, 6)',
            'rgb(55, 25, 86)',
        ],

        borderColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)',
            'rgb(255, 29, 142)',
            'rgb(0, 122, 35)',
            'rgb(25, 05, 86)',
            'rgb(0, 9, 82)',
            'rgb(4, 162, 23)',
            'rgb(255, 25, 6)',
            'rgb(55, 25, 86)',
        ],
        borderWidth: 1
        },
        ],
    },
    options: {
        title: {
            display: true,
            title: 'Expenses per category',
        }
    },
    });
}

const getChartData = () => {
    fetch('/expense_category_summary')
    .then((res) => res.json())
    .then((results) => {
        console.log(results);

        const category_data = results.expense_category_data;
        const [labels, data] = [
            Object.keys(category_data), 
            Object.values(category_data), 
        ] 
        renderChart(data, labels)
    })  
}

document.onload = getChartData();