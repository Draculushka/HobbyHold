/* HobbyHold — shared utilities */

function previewImage(input, previewId) {
    var preview = document.getElementById(previewId);
    var container = document.getElementById(previewId + 'Container');
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            container.classList.remove('hidden');
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function previewVideo(input, previewId) {
    var preview = document.getElementById(previewId);
    var container = document.getElementById(previewId + 'Container');
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            container.classList.remove('hidden');
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function handleUploadState(btnId) {
    var btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Загрузка...';
    }
}

function openImage(src) {
    var modal = document.getElementById('imageModal');
    var img = document.getElementById('modalImg');
    img.src = src;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.focus();
}

function closeImageModal() {
    var modal = document.getElementById('imageModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

function toggleSidebar() {
    var content = document.getElementById('sidebar-content');
    var btn = document.getElementById('toggle-sidebar');
    if (content && btn) {
        content.classList.toggle('hidden');
        btn.setAttribute('aria-expanded', content.classList.contains('hidden') ? 'false' : 'true');
    }
}

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeImageModal();
    }
});
