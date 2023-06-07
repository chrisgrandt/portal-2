// $(document).ready( function() {

//     $("#about-btn").click( function(event) {
//         alert("You clicked the button using JQuery!");
//     });
// });

// $("p").hover( function() {
//     $(this).css('color', 'red');
// },
// function() {
//     $(this).css('color', 'black');
// });

$('#selectionform').on('shown.bs.collapse',function(){
    $('#collapse-btn').text("Hide \u25B2")
    })

$('#selectionform').on('hidden.bs.collapse',function(){
    $('#collapse-btn').text("Show \u25BC")
});

$(document).ready(function () {

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

});

$(document).ready(function () {

    $('.btn').click(function(){
        $(this).toggleClass('active');
     })

});


// $(document).ready(function(){
//    $(".dataframe").attr('id', 'table');
//    $("#table").attr("data-toggle", "table");
//    $("#table").attr("data-sortable", "true");
//    $("#table").attr("data-search", "true");
//    $("#table").attr("data-show-fullscreen", "true");
//    $("#table").attr("data-height", "800");

// });



   
