function dancingNotes(){
  for (var i = 0; i < 24; i++) {
    var x = $('li')[i];
    $(x).css('-webkit-animation', 'music 1s ' + i + '00ms  ease-in-out both infinite');
  }
}

window.onload = function (){

    dancingNotes();
}