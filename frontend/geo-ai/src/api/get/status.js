export const fetchStatus = async () => {
    const response = await fetch('http://localhost:1001/')
    const data = await response.json()
    return data
}