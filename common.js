/* Build DID Method table using JSON data */
async function buildDidMethodTables(config) {
  const {document} = window;
  const response = await fetch('methods/index.json');
  if(response.status !== 200) {
    throw new Error('Failed retrieve DID Method index.json file.');
  }
  const allMethods = await response.json();

  // set up the API summary table headers
  const table = document.getElementById('did-method-table');
  const tableHeader = document.createElement('thead');
  tableHeader.innerHTML = '<th>DID&nbsp;Method</th><th>Registry</th>' +
    '<th>Contact</th>';
  table.appendChild(tableHeader);

  // summarize each API endpoint
  const tableBody = document.createElement('tbody');
  for(const method of allMethods) {
    const tableRow = document.createElement('tr');
    const {name, verifiableDataRegistry, contactEmail, contactName,
      contactWebsite, specification} = method;
    let contactInfo = contactName;
    if(contactEmail) {
      contactInfo += ` (<a href="mailto:${contactEmail}">email</a>)`;
    }
    if(contactWebsite) {
      contactInfo += ` (<a href="${contactWebsite}">website</a>)`;
    }
    tableRow.innerHTML =
      `<td><a href="${specification}">${name}</a></td>` +
      `<td>${verifiableDataRegistry}</td>` +
      `<td>${contactInfo}</td>`;
    tableBody.appendChild(tableRow);
  }
  table.appendChild(tableBody);

}

window.buildDidMethodTables = buildDidMethodTables;
