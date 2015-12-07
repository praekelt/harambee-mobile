$(document).ready(function() {

    var img = $("<img id='menu-link-image'>");
    img.attr('src', '/static/img/icn_menu_white_small.png');

    var menuLink = $("#menu-link");
    if (menuLink.attr("href") == "/login"){
        menuLink.removeClass("menu-link");
        menuLink.addClass("menu-link-span");
        menuLink.text('');
        img.appendTo(menuLink);
    }
    else {
        var span = $("<span id='menu-link-span'></span>");
        span.appendTo($('#icons'));
        span.addClass("menu-link-span");
        img.appendTo($('#menu-link-span'));
        img.addClass('hand-pointer');
        img.addClass('menu-link-image');
        menuLink.remove();
    }

    $("#menu").hide();
    $("#menu").insertBefore("#footer");

    var menuLinkHelper = document.getElementById("menu-link-image");
    menuLinkHelper.onclick = function() {
        if (!$("#menu-link").length) {
            if ($("#menu").is(":visible") == false)
            {
                $("#menu").show();
                $("#content").hide();
                $("#search-container").hide();
            }
            else
            {
                $("#menu").hide();
                $("#content").show();
                $("#search-container").show();
            }
        }
        else {
            window.location ="/";
        }
    };
});
