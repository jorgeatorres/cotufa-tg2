$(function(){
    $('ol.movielist > li').click(function(e){
        $this = $(this);
        
        $this.toggleClass('expanded');
        $this.find('div.moviedata').load($this.attr('rel'));
        $this.find('div.moviedata').toggle();
    });

    $('ol.movielist > li div.moviedata').click(function(e){
        e.stopPropagation();
    });
    
});

function expand_movie_cast(obj) {
    $cast = $(obj).parents('ul.castlist')
    
    $cast.children('li.morecast').remove();
    $cast.children('li').show();
    
    return false;
}
