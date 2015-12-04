$(document).ready(function() {
    $("#header-container").addClass("header-container-smart");
    $("#title-container").addClass("title-container-smart");
    $("#title-container").insertBefore("#icon-container");

    $("#icon-container").addClass("float-right");
    $("#icon-container").addClass("icon-container-smart");

    var img = $("<img id='menu-link-image'>");
    img.attr('src', '/static/img/icn_menu_white_small.png');

    var menuLink = $("#menu-link");
    if (menuLink.attr("href") == "/login"){
        menuLink.removeClass("menu-link");
        menuLink.addClass("menu-icon");
        menuLink.addClass("menu-icon-margin");
        menuLink.text('');
        img.appendTo(menuLink);
    }
    else {
        img.appendTo($('#icon-container'));
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
