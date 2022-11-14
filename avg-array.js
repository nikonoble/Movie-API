const getAverage = arr => {
    // sum the values from the array
    const reducer = (total, currentValue) => total + currentValue;
    const sum = arr.reduce(reducer)
    
    // get the length of the array
    
    // divide the array sum by the length
    return sum / arr.length;
    
    
}

getAverage([1, 2, 3, 4, 5]);


const headingGenerator = (title, typeOfHeading) => {
    return `
        <h$ {typeOfHeading}>${title}</h${typeOfHeading}>
    `
}

headingGenerator('Greetings', 2)
headingGenerator('Greetings', 1)