async function getDanmus() {

    const response = await fetch('/api/danmus');
    const data = await response.json();

    const danmus = data.data;


    return {
        result: 0,
        msg: "no error",
        data: danmus
    };
}