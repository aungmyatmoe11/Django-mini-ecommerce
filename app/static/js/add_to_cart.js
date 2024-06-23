document.addEventListener("DOMContentLoaded", function () {
  const removeCartButtons = document.querySelectorAll(".cart-cancel");

  removeCartButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const pid = this.getAttribute("pid");

      const body = JSON.stringify({
        quantity: 1,
        type: "remove",
        product_id: pid
      });

      changeCartQuantity(body)
      .then((result) => {
        const productCart= document.getElementById(`${pid}_cart`)

        if(productCart){
          productCart.remove()
        }
        changeFees(result)
        // Handle the result, update the UI if necessary
      });
    });
  });

});

const changeQuantity = (product_id,action_type)=>{
  const input = document.getElementById(`${product_id}_input`);
  const cartQty = document.getElementById(`${product_id}_cart_quantity`);
  console.log(cartQty);

  const body = JSON.stringify({
    quantity: 1,
    type: action_type,
    product_id: product_id,
  });

  changeCartQuantity(body)
      .then((result) => {
        if(input){
          input.value = result?.quantity ?? 1
          cartQty.innerText = result?.quantity ?? 1
        }
        changeFees(result)
      });
}

const changeFees = (result) => {
  const subTotal = document.querySelector(`#sub_total`)
  const totalAmount = document.querySelector(`#total_amount`)
  const shippingFee = document.querySelector(`#shipping_fee`)

  subTotal.innerText = parseInt(result?.products_amount);
  shippingFee.innerText = parseInt(result?.products_amount);
  totalAmount.innerText = parseInt(result?.total_amount);
}


const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

const csrftoken = getCookie('csrftoken');

const changeCartQuantity = async (data) => {
  try {
    const response = await fetch(`/add-to-cart-quantity/`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: data,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error);
    }

    return await response.json();
  } catch (error) {
    console.error("Error:", error);
    return { error: error.message };
  }
};
