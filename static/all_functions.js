// Remove flash
function removeFlash(){
    const element = document.getElementById("div_flash");
    element.remove();
}

// Search in table of data
function tableSearch(){
    let input, table, filt, val, tr, td;

    input = document.getElementById("txtSearch");
    filt = input.value.toUpperCase();

    table = document.getElementById("tblData");
    tr = table.getElementsByTagName("tr");

    for(var ctr = 0; ctr < tr.length; ctr++){
        td = tr[ctr].getElementsByTagName("td")[2];

        if(td){
            val = td.textContent || td.innerText;

            if(val.toUpperCase().indexOf(filt) > -1){
                tr[ctr].style.display = "";
            }
            else{
                tr[ctr].style.display = "none";
            }
        }
    }
}