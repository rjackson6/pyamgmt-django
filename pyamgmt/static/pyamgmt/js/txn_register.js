// eslint-disable-next-line @typescript-eslint/no-unused-vars
const TxnRegister = (function TxnRegister() {
    const txn_entry = document.getElementById('txn-entry');
    const $txn_entry = $(txn_entry);
    const $txn_entry_form = $('<form></form>')
        .attr({'id': 'txn-entry-form', 'method': 'post'});
    const $txn_fieldset = $('<fieldset></fieldset>')
        .prop({'class': 'grid'});
    $txn_fieldset.append(
        $('<legend></legend>').text('Transaction')
    );
    const $txn_line_item_fieldset = $('<fieldset></fieldset>')
        .prop({'class': 'grid col4'});
    $txn_line_item_fieldset.append(
        $('<legend></legend>').text('Line Items')
    );
    $txn_line_item_fieldset.append(
        $('<div></div>').append(
            $('<span></span>').text('Account'),
            $('<span></span>').text('Debit'),
            $('<span></span>').text('Credit'),
            $('<span></span>').text('Memo')
        )
    );

    const createTxnEntryForm = function createTxnEntryForm() {
        $txn_entry_form.append(
            $txn_fieldset, $txn_line_item_fieldset
        );
        $txn_fieldset.append(
            $('<label></label>').text('Date'),
            $('<input>'),
            $('<label></label>').text('Payee'),
            $('<input>')
        );
        $txn_entry.append($txn_entry_form);
        addTxnLineItem();
    };

    const addTxnLineItem = function addTxnLineItem() {
        let $line_item = $('<div></div>').prop({'class': 'entry'});
        let $account = $('<input>');
        // let $account = $('<select></select>');
        let $debit_amount = $('<input>');
        let $credit_amount = $('<input>');
        let $memo = $('<input>');
        let $add = $('<button>').attr({'type': 'button'}).text('Add Another');
        $line_item.append(
            $account, $debit_amount, $credit_amount, $memo,
            $add
        );
        $txn_line_item_fieldset.append($line_item);
        // $account.select2();
        return $line_item;
    };

    return {
        init: function init() {
            if (!window.jQuery) {
                console.log('jQuery not loaded');
                return false;
            }
            createTxnEntryForm();
            // Test code here
        }
    };
})();

$(function(){
    TxnRegister.init();
});
