async function getDanmus() {

    const response = await fetch('/api/danmus');
    const data = await response.json();

    const danmus = data.data;


    return {
        code: 0,
        msg: "no error",
        data: danmus
    };
}

async function getLastTalk() {

    const response = await fetch('/api/last-talk');
    const data = await response.json();

    const code = data.code;

    if (code !== 0) {
        return {
            code: code,
            msg: "error",
            data: null
        };
    }

    const lastTalk = data.data;


    return {
        code: 0,
        msg: "no error",
        data: lastTalk
    };
}

