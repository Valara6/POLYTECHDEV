document.addEventListener('DOMContentLoaded', function () {
    let deleteAuctionModal = document.querySelector('#deleteAuction');

    deleteAuctionModal.addEventListener('show.bs.modal', function(event) {
        let button = event.relatedTarget; // Кнопка, вызвавшая модальное окно
        let form = deleteAuctionModal.querySelector('.modal-form');
        let auction = deleteAuctionModal.querySelector('.auction-title');

        // Подставляем действие (action) формы
        form.action = button.dataset.action;

        // Получаем название аукциона из первой ячейки строки
        auction.textContent = button.closest('tr').querySelector('td:first-child').textContent;
    });
});
