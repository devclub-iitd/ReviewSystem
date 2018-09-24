$(document).ready(function(){
    console.log("yay");
    $("input").addClass("form-control");
    $(".edit-form").hide();
    $(".exit").hide();
    $(".actual_work").hide();
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
      $(".actual_work").show();
      $(".long_work").hide();
      //alert($(".actual_work").text());
    });

    $(".actual_work").on("click",function(){
      $(".long_work").show();
      $(".actual_work").hide();
    });

    $(".long_work").mouseover(function(){
      $(this).css('color','blue');
      $(this).css('cursor','pointer');
    });
    $(".long_work").mouseout(function(){
      $(this).css('color','black');
    });
    $(".close-icon").mouseover(function(){
      $(this).css('cursor','pointer');
    });
    $(".close-icon").on("click",function(){
      $(this).closest(".work-card").hide();
      delete_work();
    });
});
function delete_work() {
    console.log("create post is working!"); // sanity check
    //console.log($('#post-text').val());
    var work = $(this).attr('id');
    console.log( '{{ csrf_token }}' );
    $.ajax({
      url:"", //Enter the url of Edit View's POST,
      type: "POST",
      dataType: "json",
      data: {
        "work_delete" :work,
        "csrfmiddlewaretoken" :'{{ csrf_token }}',
      },
      success: function(){
        console.log("Successsful Ajax");
      },
      error: function(){
        console.log("Unsuccessful Ajax");
      }
    });
};
