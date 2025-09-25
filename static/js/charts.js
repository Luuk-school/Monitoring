// Chart.js configuratie voor system monitoring

let cpuMemoryChart;
let diskNetworkChart;

function initCharts(historyData) {
    // CPU & Memory Chart
    const ctx1 = document.getElementById('cpuMemoryChart').getContext('2d');
    cpuMemoryChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: historyData.timestamps,
            datasets: [{
                label: 'CPU %',
                data: historyData.cpu,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Memory %',
                data: historyData.memory,
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    ticks: {
                        maxTicksLimit: 10
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });

    // Disk & Network Chart
    const ctx2 = document.getElementById('diskNetworkChart').getContext('2d');
    diskNetworkChart = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: historyData.timestamps,
            datasets: [{
                label: 'Disk %',
                data: historyData.disk,
                borderColor: '#ffc107',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Network MB/s',
                data: historyData.network,
                borderColor: '#17a2b8',
                backgroundColor: 'rgba(23, 162, 184, 0.1)',
                fill: true,
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return value + ' MB';
                        }
                    }
                },
                x: {
                    ticks: {
                        maxTicksLimit: 10
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label;
                            let value = context.parsed.y.toFixed(1);
                            if (label.includes('Disk')) {
                                return label + ': ' + value + '%';
                            } else {
                                return label + ': ' + value + ' MB';
                            }
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Update charts met nieuwe data
function updateCharts(newData) {
    if (cpuMemoryChart && diskNetworkChart) {
        // Update CPU & Memory chart
        cpuMemoryChart.data.labels = newData.timestamps;
        cpuMemoryChart.data.datasets[0].data = newData.cpu;
        cpuMemoryChart.data.datasets[1].data = newData.memory;
        cpuMemoryChart.update('none');

        // Update Disk & Network chart
        diskNetworkChart.data.labels = newData.timestamps;
        diskNetworkChart.data.datasets[0].data = newData.disk;
        diskNetworkChart.data.datasets[1].data = newData.network;
        diskNetworkChart.update('none');
    }
}

// Resize charts wanneer window grootte verandert
window.addEventListener('resize', function() {
    if (cpuMemoryChart) {
        cpuMemoryChart.resize();
    }
    if (diskNetworkChart) {
        diskNetworkChart.resize();
    }
});

// Status indicator kleuren gebaseerd op waarden
function getStatusClass(value, type) {
    if (type === 'cpu' || type === 'memory') {
        if (value < 70) return 'status-good';
        if (value < 90) return 'status-warning';
        return 'status-danger';
    } else if (type === 'disk') {
        if (value < 80) return 'status-good';
        if (value < 95) return 'status-warning';
        return 'status-danger';
    }
    return 'status-good';
}

// Formatteren van bytes naar leesbare eenheden
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}