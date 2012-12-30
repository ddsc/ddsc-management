from django.db.models import Q

# Never return more then MAX_RECORDS records
MAX_RECORDS = 10000

def get_datatables_records(request, querySet, allowedColitems=[]):
    """
    Usage:
        querySet: query set to draw data from.
        allowedColitems: optional whitelist of field names allowed to be displayed.
    """
    allowedColitems = list(allowedColitems)
    if 'pk' not in allowedColitems:
        # pk is always allowed
        allowedColitems.append('pk')

    # Get the number of columns
    cols = int(request.GET.get('iColumns', 0))
    # Safety measure. If someone messes with iDisplayLength manually, we clip it to the max value of 100.
    iDisplayLength =  min(int(request.GET.get('iDisplayLength', 10)), MAX_RECORDS)
    if iDisplayLength == -1:
        # Occurs for example in the print view of DataTables
        iDisplayLength = MAX_RECORDS
    # Where the data starts from (page)
    startRecord = int(request.GET.get('iDisplayStart', 0))
    # Where the data ends (end of page)
    endRecord = startRecord + iDisplayLength

    # Parse sColumns
    colitems = request.GET.get('sColumns')
    if not colitems:
        colitems = querySet.model._meta.get_all_field_names()
    else:
        colitems = colitems.split(',')
    # pk is always returned
    if 'pk' not in colitems:
        colitems.append('pk')
    # Filter colitems
    invalidColitems = set(colitems).difference(set(allowedColitems))
    # Just remove the disallowed columns, while maintaining the list order
    for col in invalidColitems:
        colitems.remove(col)
    # Helper dict
    columnIndexNameMap = dict([(i, colitems[i]) for i in range(len(colitems))])
    # Pass resulting sColumns
    sColumns = ",".join(map(str, colitems))

    # Ordering data
    iSortingCols = int(request.GET.get('iSortingCols', 0))
    aSortingCols = []

    if iSortingCols:
        for sortedColIndex in range(0, iSortingCols):
            sortedColID = int(request.GET.get('iSortCol_' + str(sortedColIndex), 0))
            # Let's make sure the column is sortable first
            if request.GET.get('bSortable_{0}'.format(sortedColID), 'false')  == 'true':
                # Make sure column is part of the results
                if sortedColID in columnIndexNameMap:
                    sortedColName = columnIndexNameMap[sortedColID]
                    sortingDirection = request.GET.get('sSortDir_' + str(sortedColIndex), 'asc')
                    if sortingDirection == 'desc':
                        sortedColName = '-' + sortedColName
                    aSortingCols.append(sortedColName)
        querySet = querySet.order_by(*aSortingCols)

    # Determine which columns are searchable
    searchableColumns = []
    for col in range(0, cols):
        if request.GET.get('bSearchable_{0}'.format(col), False) == 'true' and \
           col in columnIndexNameMap:
            searchableColumns.append(columnIndexNameMap[col])

    # Apply filtering by value sent by user
    customSearch = request.GET.get('sSearch', '').encode('utf-8');
    if customSearch != '':
        outputQ = None
        first = True
        for searchableColumn in searchableColumns:
            kwargz = {
                searchableColumn + "__icontains": customSearch
            }
            outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)
        querySet = querySet.filter(outputQ)

    # Individual column search
    outputQ = None
    for col in range(0, cols):
        if request.GET.get('sSearch_{0}'.format(col), False) > '' and \
           request.GET.get('bSearchable_{0}'.format(col), False) == 'true' and \
           col in columnIndexNameMap:
            kwargz = {
                columnIndexNameMap[col] + "__icontains": request.GET['sSearch_{0}'.format(col)]
            }
            outputQ = outputQ & Q(**kwargz) if outputQ else Q(**kwargz)
    if outputQ: querySet = querySet.filter(outputQ)

    # Count how many records match the final criteria
    iTotalRecords = iTotalDisplayRecords = querySet.count()
    # Get the slice
    querySet = querySet[startRecord:endRecord]
    # Required echo response
    sEcho = int(request.GET.get('sEcho', 0))

    aaData = []
    '''
    a = querySet.values(*colitems)
    for row in a:
        rowkeys = row.keys()
        rowvalues = row.values()
        rowlist = []
        for col in range(0, len(colitems)):
            for idx, val in enumerate(rowkeys):
                if val == colitems[col]:
                    rowlist.append(str(rowvalues[idx]))
        aaData.append(rowlist)
    '''

    a = querySet.values(*colitems)
    for row in a:
        rowkeys = row.keys()
        rowvalues = row.values()
        # Requested order of columns can be different than the
        # order in the database, so match them up.
        aaData.append([row[colname] for colname in colitems])

    response_dict = {}
    response_dict.update({'aaData': aaData})
    response_dict.update({
        'sEcho': sEcho,
        'iTotalRecords': iTotalRecords,
        'iTotalDisplayRecords': iTotalDisplayRecords,
        'sColumns': sColumns
    })
    return response_dict
