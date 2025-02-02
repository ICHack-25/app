export class DataObject {
    name: string;
    file_type: string;
    file_path: string;

    constructor(name: string, file_type: string, file_path: string) {
        this.name = name;
        this.file_type = file_type;
        this.file_path = file_path;
    }

    toPlainObject() {
        return {
            name: this.name,
            file_type: this.file_type,
            file_path: this.file_path
        };
    }
}


export interface NodeData {
    type: string;
    url: string;
}

export interface Node {
    id: string;
    label: string;
    data: NodeData;
}

export interface Edge {
    id: string;
    source: string;
    target: string;
    label: string;
}

// export const convertToNodes = (dataObjects: DataObject[]): Node[] => {
//     return dataObjects.map((dataObj, index) => ({
//         id: `n-${index + 1}`, // Creating unique ID for each node
//         label: dataObj.name,   // Using the name as the label
//         data: {
//             type: dataObj.file_type,  // Mapping file_type to type
//             url: dataObj.file_path   // Mapping file_path to url
//         }
//     }));
// };

// Modify the function to take an array of plain objects
export const convertToNodes = (dataObjects: { name: string; file_type: string; file_path: string }[]): Node[] => {
    return dataObjects.map((dataObj, index) => ({
        id: `n-${index + 1}`, // Creating unique ID for each node
        label: dataObj.name,   // Using the name as the label
        data: {
            type: dataObj.file_type,  // Mapping file_type to type
            url: dataObj.file_path   // Mapping file_path to url
        }
    }));
};

export interface NetworkProps {
    data: { name: string; file_type: string; file_path: string }[];
}

export function getRandomNewsProvider() {
    const newsProviders = [
        "BBC News",
        "CNN",
        "Reuters",
        "The Guardian",
        "The New York Times",
        "Al Jazeera",
        "The Washington Post",
        "Bloomberg",
        "Fox News",
        "The Independent",
        "Associated Press",
        "The Times",
        "USA Today",
        "The Huffington Post",
        "NPR",
        "ABC News",
        "Sky News",
        "Newsweek",
        "The Telegraph",
        "Financial Times",
        "The Wall Street Journal",
        "The Daily Mail",
        "Guardian Australia",
        "Le Monde",
        "El País",
        "Le Figaro",
        "Der Spiegel",
        "The Sydney Morning Herald",
        "Time",
        "Forbes",
        "The Sun",
        "Reuters UK",
        "The Atlantic",
        "Business Insider",
        "The New Yorker",
        "Politico",
        "The Independent UK",
        "CNA",
        "RT",
        "Fox Business",
        "The Economist",
        "The Nation",
        "Deutsche Welle",
        "HuffPost",
        "Channel NewsAsia",
        "The Times of India",
        "The Japan Times",
        "South China Morning Post",
        "Global Times",
        "The Korea Times",
        "The Hindu"
    ];

    // Randomly select a news provider from the list
    const randomIndex = Math.floor(Math.random() * newsProviders.length);
    return newsProviders[randomIndex];
}
