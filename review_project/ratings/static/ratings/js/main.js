$(document).ready(function(){
    console.log("yay");
    $("input").addClass("form-control");
    $(".edit-form").hide();
    $(".exit").hide();
    $(".actual_work").hide()
    $(".editable").on("click",function(){
        $(".edit-form").show();
        $(".no-edit").hide();
        $(".exit").show();
        $(".editable").hide();
    });
    $(".exit").on("click",function(){
        $(".edit-form").hide();
        $(".no-edit").show();
        $(".editable").show();
        $(".exit").hide();
    })

    $(".long_work").on("click",function(){
      //$(".actual_work").show();
      //$(".long_work").hide();
      alert($(".actual_work").text());
    });


    $(".long_work").mouseover(function(){
      $(this).css('color','blue');
      $(this).css('cursor','pointer');
    });
    $(".long_work").mouseout(function(){
      $(this).css('color','black');
    });
});
