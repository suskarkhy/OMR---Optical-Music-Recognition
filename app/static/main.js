const allowed_formats = ["png", "jpg", "jpeg"];

function check_format(fname){
    const format = fname.split('.').pop().toLowerCase();
    return allowed_formats.includes(format);
}

$(function(){
    $("#upload-file").on("input", function(e){
        let file = e.target.files[0];
        if (check_format(file["name"])){
            let formdata = new FormData();
            formdata.append("file", file);

            $.ajax({
                url:"/",
                type:"POST",
                data:formdata,
                processData:false,
                contentType:false,
                success:function(data, status){
                    
                    let divimg = $('<div class="my-2" style="border: 2px solid black; border-radius: 5px; overflow:hidden;"></div>');
                    
                    divimg.append($('<img class="img-fluid" style="width:60vh;" src="'+data["img_url"]+'"></img>'));
                    divimg.append($('<midi-player src="'+data["midi_url"]+'" sound-font></midi-player>'));

                    $("#output").prepend(divimg);
                },
                error: function(status, errorThrown){console.log("ERROR!!!!");}
            });
        }
    });
});