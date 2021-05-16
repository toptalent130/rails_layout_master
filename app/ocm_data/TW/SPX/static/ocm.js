// $(document).ready(function(){
//     // $(".exp_show").click(function(){
//         console.log(">>>>>>>>>>>>asdfdfdfd")
//     // })
// })
$(document).on("click", ".exp_show", function (e) {
    e.preventDefault();
    // $("#slider-exp .rc-slider-dot-active").removeClass('rc-slider-dot-active')
    // $("#slider-exp .rc-slider-dot").eq(3).addClass('rc-slider-dot-active')  
    alert($("#slider-exp").slider("value"))
});