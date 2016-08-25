function checkFileSize(file, maxSizeMB) {
    maxSizeMB = maxSizeMB || 30;

    // 사이즈체크
    var maxSize  = maxSizeMB * 1024 * 1024;
    var fileSize = 0;
    var browser = navigator.appName;

	if (browser=="Microsoft Internet Explorer") {
	    // 익스플로러일 경우
		var oas = new ActiveXObject("Scripting.FileSystemObject");
		fileSize = oas.getFile(file.value).size;
	} else {
	    // 익스플로러가 아닐경우
		fileSize = file.files[0].size;
	}

    if (fileSize > maxSize) {
        return false;
    }

    return true;
}
