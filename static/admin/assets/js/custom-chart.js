// (function ($) {
//     "use strict";

//     // Define a function to fetch data from the server
//     function fetchData() {
//         $.ajax({
//             url: "{% url 'fetch_data_endpoint' %}",  // Replace 'fetch_data_endpoint' with your actual endpoint
//             method: '',
//             success: function(response) {
//                 // Update chart data with the received data
//                 updateChart(response);
//             },
//             error: function(xhr, status, error) {
//                 console.error(xhr.responseText);
//             }
//         });
//     // }

//     // Define a function to update chart data
//     function updateChart(data) {
//         if ($('#myChart').length) {
//             var ctx = document.getElementById('myChart').getContext('2d');
//             var chart = new Chart(ctx, {
//                 type: 'line',
//                 data: {
//                     labels: data.labels,
//                     datasets: [
//                         {
//                             label: 'Orders',  // Replace 'Sales' with 'Orders'
//                             tension: 0.3,
//                             fill: true,
//                             backgroundColor: 'rgba(44, 120, 220, 0.2)',
//                             borderColor: 'rgba(44, 120, 220)',
//                             data: data.orders  // Provide the orders data
//                         },
//                         {
//                             label: 'Total Revenue',  // Replace 'Visitors' with 'Total Revenue'
//                             tension: 0.3,
//                             fill: true,
//                             backgroundColor: 'rgba(4, 209, 130, 0.2)',
//                             borderColor: 'rgb(4, 209, 130)',
//                             data: data.total_revenue  // Provide the total revenue data
//                         },
//                         {
//                             label: 'Products',
//                             tension: 0.3,
//                             fill: true,
//                             backgroundColor: 'rgba(380, 200, 230, 0.2)',
//                             borderColor: 'rgb(380, 200, 230)',
//                             data: data.products  // Provide the products data
//                         }
//                     ]
//                 },
//                 options: {
//                     plugins: {
//                         legend: {
//                             labels: {
//                                 usePointStyle: true,
//                             },
//                         }
//                     }
//                 }
//             });
//         }
//     }

//     // Fetch data on document ready
//     $(document).ready(function () {
//         fetchData();
//     });
// })(jQuery);
