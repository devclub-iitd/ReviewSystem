$(document).ready(function(){
    console.log("yay"); 
    $("input").addClass("form-control");
    $(".edit-form").hide();
    $(".editable").on("click",function(){
        console.log("Into edit");
        $(".edit-form").show();
        $(".no-edit").hide();    
    });
});