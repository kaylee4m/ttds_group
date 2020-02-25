const $http = (url, params = {}) => {
    const search = new URLSearchParams()
    for (let key in params) {
        search.append(key, params[key])
    }
    return fetch(url + '?' + search.toString()).then(res => res.json()).then(res => {
        if (res.succ) {
            return res.data
        }
        alert(res.msg || '请求错误')
    })
}