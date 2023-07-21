// Add and remove input fields for items and prices
let inputs = document.getElementById('extra-inputs');

const receiptForm = document.getElementById("receipt-form")

receiptForm.addEventListener("click", (event) => {
    if(event.target.id === 'add-item-input') {
        let inputs = document.getElementById('extra-inputs');
        
        function add(){
            var numInputs = document.getElementsByClassName('input-group').length;
            
            var input = document.createElement('div');
            input.setAttribute('class', 'input-group my-3');
            input.innerHTML = `
            <input class="form-control" id="i${numInputs+1}" name="item" placeholder="Item" required="True" type="text" value>
            <span id="label1" for="p${numInputs+1}" class="input-group-text">£</span>
            <input class="form-control" id="p${numInputs+1}" min="0" name="price" placeholder="0.00" required="True" step="0.01" style="max-width: 100px;" type="number" value>`;
            inputs.appendChild(input);
        };
        add();
    }
});

receiptForm.addEventListener("click", (event) => {
    if(event.target.id === 'remove-item-input') {
        let inputs = document.getElementById('extra-inputs');
        
        function remove(){
            inputs.removeChild(inputs.lastChild);
        };
        remove();
    }
});
