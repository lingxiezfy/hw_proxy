function openScan() {
    var scrWidth=screen.availWidth;
    var scrHeight=screen.availHeight;
    var win =window.open('statusscan/index.html','statusscan','height=100, width=100, top=0,left=0,toolbar=no, menubar=no, scrollbars=yes, resizable=no, location=no, status=no');
    win.moveTo(0,0);
    win.resizeTo(scrWidth,scrHeight);
}
