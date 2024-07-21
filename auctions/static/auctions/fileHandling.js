document.addEventListener('DOMContentLoaded', (event) => {
    function updateFileList(input, listElement) {
        const files = input.files;
        let fileList = '';
        for (let i = 0; i < files.length; i++) {
            fileList += `<p>${files[i].name}</p>`;
        }
        listElement.innerHTML = fileList;
    }

    const imageInput = document.getElementById('id_images');
    const videoInput = document.getElementById('id_videos');
    const imageFileList = document.getElementById('imageFileList');
    const videoFileList = document.getElementById('videoFileList');

    imageInput.addEventListener('change', function() {
        updateFileList(this, imageFileList);
    });

    videoInput.addEventListener('change', function() {
        updateFileList(this, videoFileList);
    });
});

// function initializeFileListUpdater() {
//     function updateFileList(input, listElement) {
//         const files = input.files;
//         let fileList = '';
//         for (let i = 0; i < files.length; i++) {
//             fileList += `<p>${files[i].name}</p>`;
//         }
//         listElement.innerHTML = fileList;
//     }

//     // Find all file inputs with data-file-list attribute
//     const fileInputs = document.querySelectorAll('input[type="file"][data-file-list]');
    
//     fileInputs.forEach(input => {
//         const listElementId = input.getAttribute('data-file-list');
//         const listElement = document.getElementById(listElementId);
        
//         if (listElement) {
//             input.addEventListener('change', function() {
//                 updateFileList(this, listElement);
//             });
//         }
//     });
// }

// document.addEventListener('DOMContentLoaded', initializeFileListUpdater);