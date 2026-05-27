      const state = {
        datasets: [],
        filtered: [],
        selectedId: null,
        datasetPanelHidden: false,
        itemsByDatasetId: {},
        itemsPaginationByDatasetId: {},
        metadataByDatasetId: {},
      }

      const catalogUrl = 'stac/catalog.json'
      const statusText = document.getElementById('statusText')
      const catalogTitle = document.getElementById('catalogTitle')
      const datasetList = document.getElementById('datasetList')
      const datasetCount = document.getElementById('datasetCount')
      const detailsPanel = document.getElementById('detailsPanel')
      const searchInput = document.getElementById('searchInput')
      const reloadBtn = document.getElementById('reloadBtn')
      const browserGrid = document.querySelector('.browser-grid')
      const listPanel = document.querySelector('.list-panel')

      const toggleDatasetsBtn = document.createElement('button')
      toggleDatasetsBtn.id = 'toggleDatasetsBtn'
      toggleDatasetsBtn.className = 'btn btn-outline-primary btn-sm'
      toggleDatasetsBtn.textContent = 'Hide Datasets'
      document.querySelector('.actions').appendChild(toggleDatasetsBtn)

      // Modal page for items and metadata display
      let itemsModalBackdrop = null
      let itemsModalDatasetTitle = null
      let itemsModalDatasetId = null
      let itemsModalBody = null
      let metadataModalBackdrop = null
      let metadataModalDatasetTitle = null
      let metadataModalDatasetId = null
      let metadataModalSource = null
      let metadataModalBody = null

      function setStatus(message) {
        statusText.textContent = message
      }

      function applyDatasetPanelVisibility() {
        if (state.datasetPanelHidden) {
          listPanel.style.display = 'none'
          browserGrid.style.gridTemplateColumns = '1fr'
          toggleDatasetsBtn.textContent = 'Show List of Datasets'
        } else {
          listPanel.style.display = ''
          browserGrid.style.gridTemplateColumns = ''
          toggleDatasetsBtn.textContent = 'View Selected Dataset'
        }
      }

      // Fetch jason file and return json data if request is successful, 
      // otherwise throw an error
      async function fetchJson(url) {
        const response = await fetch(url)
        if (!response.ok) {
          throw new Error(`Request failed: ${response.status}`)
        }
        return response.json()
      }

      // Check existance
      function isExternalLink(url) {
        return /^https?:\/\//i.test(url || '')
      }

      // Check accessible
      function isOpenableLink(url) {
        if (typeof url !== 'string') return false
        const value = url.trim()
        if (!value) return false
        return !/^javascript:/i.test(value)
      }

      function isMarkedExternal(url, explicitExternal = false) {
        return explicitExternal === true
      }

      function renderOpenLinkMarkup(href, explicitExternal = false) {
        if (!href) return 'n/a'

        const externalLabel = isMarkedExternal(href, explicitExternal)
          ? ' <span class="dataset-id">(external)</span>'
          : ''

        return `<a href="${href}" target="_blank" rel="noreferrer">Open</a>${externalLabel}<div class="dataset-id">${href}</div>`
      }

      function resolveRelativeUrl(baseUrl, href) {
        if (!href) return ''

        try {
          return new URL(href, new URL(baseUrl, window.location.href)).toString()
        } catch {
          return href
        }
      }

      function getDisplayNameFromHref(href) {
        if (!href) return ''

        try {
          const parsed = new URL(href, window.location.href)
          const filename = parsed.pathname.split('/').filter(Boolean).pop()
          return filename || href
        } catch {
          const filename = href.split('/').filter(Boolean).pop()
          return filename || href
        }
      }

      // check for nc file
      function isNetcdfAsset(asset) {
        const type = `${asset?.type || ''}`.toLowerCase()
        const href = `${asset?.href || ''}`.toLowerCase()
        return type.includes('netcdf') || href.endsWith('.nc') || href.endsWith('.nc4')
      }

      function extractItemsLink(collection) {
        const links = collection?.links || []
        const found = links.find((link) => link.rel === 'items' && typeof link.href === 'string' && link.href.length > 0)
        return found?.href || ''
      }

      function extractItemLinks(collection) {
        const links = collection?.links || []
        return links
          .filter((link) => link.rel === 'item' && typeof link.href === 'string' && link.href.length > 0)
          .map((link) => link.href)
      }

      async function fetchDatasetMetadata(dataset) {
        const metadataUrl = resolveRelativeUrl(dataset.collectionUrl, './collection.json')
        const json = await fetchJson(metadataUrl)
        return {
          source: metadataUrl,
          data: json,
        }
      }

      function createMetadataModal() {
        if (metadataModalBackdrop) return

        metadataModalBackdrop = document.createElement('div')
        metadataModalBackdrop.className = 'items-modal-backdrop'
        metadataModalBackdrop.style.display = 'none'
        metadataModalBackdrop.innerHTML = `
          <div class="items-modal panel" role="dialog" aria-modal="true" aria-label="Dataset metadata">
            <div class="panel-header">
              <h3 class="mb-0" id="metadataModalTitle">Dataset Metadata</h3>
              <button class="btn btn-sm" id="closeMetadataModalBtn">Close</button>
            </div>
            <p class="dataset-id mb-1"><strong>Dataset ID:</strong> <span id="metadataModalDatasetId">n/a</span></p>
            <p class="dataset-id mb-2"><strong>Source:</strong> <span id="metadataModalSource">n/a</span></p>
            <div id="metadataModalBody"></div>
          </div>
        `

        document.body.appendChild(metadataModalBackdrop)

        metadataModalDatasetTitle = document.getElementById('metadataModalTitle')
        metadataModalDatasetId = document.getElementById('metadataModalDatasetId')
        metadataModalSource = document.getElementById('metadataModalSource')
        metadataModalBody = document.getElementById('metadataModalBody')

        const closeButton = document.getElementById('closeMetadataModalBtn')
        closeButton.addEventListener('click', closeMetadataModal)
        metadataModalBackdrop.addEventListener('click', (event) => {
          if (event.target === metadataModalBackdrop) {
            closeMetadataModal()
          }
        })
      }

      function closeMetadataModal() {
        if (!metadataModalBackdrop) return
        metadataModalBackdrop.style.display = 'none'
      }

      function renderMetadataModal(dataset, metadata, errorMessage = '') {
        createMetadataModal()

        metadataModalDatasetTitle.textContent = `${dataset.title || dataset.id} Metadata`
        metadataModalDatasetId.textContent = dataset.id || 'n/a'

        if (errorMessage) {
          metadataModalSource.textContent = 'Unavailable'
          metadataModalBody.innerHTML = `<p class="error mb-0">${errorMessage}</p>`
          metadataModalBackdrop.style.display = 'flex'
          return
        }

        metadataModalSource.textContent = metadata.source
        metadataModalBody.innerHTML = `<pre class="metadata-json">${JSON.stringify(metadata.data, null, 2)}</pre>`
        metadataModalBackdrop.style.display = 'flex'
      }

      async function openMetadataModal(dataset) {
        createMetadataModal()
        metadataModalDatasetTitle.textContent = `${dataset.title || dataset.id} Metadata`
        metadataModalDatasetId.textContent = dataset.id || 'n/a'
        metadataModalSource.textContent = 'Loading...'
        metadataModalBody.innerHTML = '<p class="mb-0">Loading metadata...</p>'
        metadataModalBackdrop.style.display = 'flex'

        if (state.metadataByDatasetId[dataset.id]) {
          renderMetadataModal(dataset, state.metadataByDatasetId[dataset.id])
          return
        }

        try {
          const metadata = await fetchDatasetMetadata(dataset)
          state.metadataByDatasetId[dataset.id] = metadata
          renderMetadataModal(dataset, metadata)
        } catch (error) {
          renderMetadataModal(dataset, null, `Unable to load metadata: ${error.message}`)
        }
      }

      function formatItemDatetime(item) {
        return item?.properties?.datetime || item?.properties?.start_datetime || 'n/a'
      }

      function flattenItemAssets(itemCollection, itemCollectionUrl) {
        const features = Array.isArray(itemCollection?.features) ? itemCollection.features : []

        return features.flatMap((feature) => {
          const assets = feature?.assets || {}
          const itemId = feature?.id || 'unknown-item'
          const itemDatetime = formatItemDatetime(feature)

          return Object.entries(assets)
            .filter(([, asset]) => typeof asset?.href === 'string' && asset.href.length > 0)
            .map(([assetKey, asset]) => {
              const resolvedHref = resolveRelativeUrl(itemCollectionUrl, asset.href)
              return {
                id: `${itemId}:${assetKey}`,
                itemId,
                itemDatetime,
                assetKey,
                title: asset.title || getDisplayNameFromHref(asset.href) || assetKey,
                href: resolvedHref,
                type: asset.type || '',
                isNetcdf: isNetcdfAsset(asset),
              }
            })
        })
      }

      function createItemsModal() {
        if (itemsModalBackdrop) return

        itemsModalBackdrop = document.createElement('div')
        itemsModalBackdrop.className = 'items-modal-backdrop'
        itemsModalBackdrop.style.display = 'none'
        itemsModalBackdrop.innerHTML = `
          <div class="items-modal panel" role="dialog" aria-modal="true" aria-label="Dataset item assets">
            <div class="panel-header">
              <h3 class="mb-0" id="itemsModalTitle">Dataset Items</h3>
              <button class="btn btn-sm" id="closeItemsModalBtn">Close</button>
            </div>
            <p class="dataset-id mb-2"><strong>Dataset ID:</strong> <span id="itemsModalDatasetId">n/a</span></p>
            <div id="itemsModalBody"></div>
          </div>
        `

        document.body.appendChild(itemsModalBackdrop)

        itemsModalDatasetTitle = document.getElementById('itemsModalTitle')
        itemsModalDatasetId = document.getElementById('itemsModalDatasetId')
        itemsModalBody = document.getElementById('itemsModalBody')

        const closeButton = document.getElementById('closeItemsModalBtn')
        closeButton.addEventListener('click', closeItemsModal)
        itemsModalBackdrop.addEventListener('click', (event) => {
          if (event.target === itemsModalBackdrop) {
            closeItemsModal()
          }
        })
      }

      function closeItemsModal() {
        if (!itemsModalBackdrop) return
        itemsModalBackdrop.style.display = 'none'
      }

      function getItemsPagination(datasetId, totalCount) {
        const current = state.itemsPaginationByDatasetId[datasetId] || { page: 1, pageSize: 25 }
        const safePageSize = Number(current.pageSize) > 0 ? Number(current.pageSize) : 25
        const totalPages = Math.max(1, Math.ceil(totalCount / safePageSize))
        const safePage = Math.min(Math.max(Number(current.page) || 1, 1), totalPages)

        const next = { page: safePage, pageSize: safePageSize }
        state.itemsPaginationByDatasetId[datasetId] = next
        return next
      }

      function renderPaginatedItemsTable(dataset, assets) {
        const pagination = getItemsPagination(dataset.id, assets.length)
        const totalPages = Math.max(1, Math.ceil(assets.length / pagination.pageSize))
        const startIndex = (pagination.page - 1) * pagination.pageSize
        const endIndex = startIndex + pagination.pageSize
        const pageAssets = assets.slice(startIndex, endIndex)

        const rows = pageAssets
          .map((asset) => {
            const typeLabel = asset.type || (asset.isNetcdf ? 'application/x-netcdf' : 'unknown')
            const typeClass = asset.isNetcdf ? 'asset-type-badge netcdf' : 'asset-type-badge'

            return `
              <tr>
                <td>${asset.itemId}</td>
                <td>${asset.itemDatetime}</td>
                <td>${asset.title}</td>
                <td><span class="${typeClass}">${typeLabel}</span></td>
                <td><a href="${asset.href}" target="_blank" rel="noreferrer">Download</a></td>
              </tr>
            `
          })
          .join('')

        itemsModalBody.innerHTML = `
          <div class="items-content">
            <div class="items-table-wrap">
              <table class="items-table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Date/Time</th>
                    <th>Asset</th>
                    <th>Type</th>
                    <th>Download</th>
                  </tr>
                </thead>
                <tbody>
                  ${rows}
                </tbody>
              </table>
            </div>
            <div class="items-pagination">
              <div class="items-pagination-status">
                Showing ${startIndex + 1}-${Math.min(endIndex, assets.length)} of ${assets.length} assets
              </div>
              <div class="items-pagination-controls">
                <label for="itemsPageSizeSelect" class="items-page-size-label">Rows:</label>
                <select id="itemsPageSizeSelect" class="form-select form-select-sm items-page-size-select">
                  <option value="10" ${pagination.pageSize === 10 ? 'selected' : ''}>10</option>
                  <option value="25" ${pagination.pageSize === 25 ? 'selected' : ''}>25</option>
                  <option value="50" ${pagination.pageSize === 50 ? 'selected' : ''}>50</option>
                  <option value="100" ${pagination.pageSize === 100 ? 'selected' : ''}>100</option>
                </select>
                <button id="itemsPrevPageBtn" class="btn btn-sm btn-outline-secondary" ${pagination.page <= 1 ? 'disabled' : ''}>Prev</button>
                <span class="items-page-indicator">Page ${pagination.page} of ${totalPages}</span>
                <button id="itemsNextPageBtn" class="btn btn-sm btn-outline-secondary" ${pagination.page >= totalPages ? 'disabled' : ''}>Next</button>
              </div>
            </div>
          </div>
        `

        const prevBtn = document.getElementById('itemsPrevPageBtn')
        const nextBtn = document.getElementById('itemsNextPageBtn')
        const pageSizeSelect = document.getElementById('itemsPageSizeSelect')

        if (prevBtn) {
          prevBtn.addEventListener('click', () => {
            state.itemsPaginationByDatasetId[dataset.id] = {
              ...pagination,
              page: Math.max(1, pagination.page - 1),
            }
            renderPaginatedItemsTable(dataset, assets)
          })
        }

        if (nextBtn) {
          nextBtn.addEventListener('click', () => {
            state.itemsPaginationByDatasetId[dataset.id] = {
              ...pagination,
              page: Math.min(totalPages, pagination.page + 1),
            }
            renderPaginatedItemsTable(dataset, assets)
          })
        }

        if (pageSizeSelect) {
          pageSizeSelect.addEventListener('change', (event) => {
            const nextPageSize = Number(event.target.value) || 25
            state.itemsPaginationByDatasetId[dataset.id] = {
              page: 1,
              pageSize: nextPageSize,
            }
            renderPaginatedItemsTable(dataset, assets)
          })
        }
      }

      function renderItemsModal(dataset, assets, errorMessage = '') {
        createItemsModal()
        itemsModalDatasetTitle.textContent = `${dataset.title || dataset.id} Items`
        itemsModalDatasetId.textContent = dataset.id || 'n/a'

        if (errorMessage) {
          itemsModalBody.innerHTML = `<p class="error mb-0">${errorMessage}</p>`
          itemsModalBackdrop.style.display = 'flex'
          return
        }

        if (!assets || assets.length === 0) {
          itemsModalBody.innerHTML = '<p class="empty mb-0">No downloadable assets were found.</p>'
          itemsModalBackdrop.style.display = 'flex'
          return
        }

        renderPaginatedItemsTable(dataset, assets)

        itemsModalBackdrop.style.display = 'flex'
      }

      async function openItemsModal(dataset) {
        const hasItemsCollection = typeof dataset?.itemsLink === 'string' && dataset.itemsLink.length > 0
        const hasItemLinks = Array.isArray(dataset?.itemLinks) && dataset.itemLinks.length > 0
        if (!hasItemsCollection && !hasItemLinks) {
          return
        }

        createItemsModal()
        itemsModalDatasetTitle.textContent = `${dataset.title || dataset.id} Items`
        itemsModalDatasetId.textContent = dataset.id || 'n/a'
        itemsModalBody.innerHTML = '<p class="mb-0">Loading item assets...</p>'
        itemsModalBackdrop.style.display = 'flex'

        if (state.itemsByDatasetId[dataset.id]) {
          renderItemsModal(dataset, state.itemsByDatasetId[dataset.id])
          return
        }

        try {
          let assets = []

          if (hasItemsCollection) {
            const itemsUrl = resolveRelativeUrl(dataset.collectionUrl, dataset.itemsLink)
            const itemCollection = await fetchJson(itemsUrl)
            assets = flattenItemAssets(itemCollection, itemsUrl)
          } else {
            const itemUrls = dataset.itemLinks.map((href) => resolveRelativeUrl(dataset.collectionUrl, href))
            const itemResponses = await Promise.all(itemUrls.map((url) => fetchJson(url)))
            assets = itemResponses.flatMap((item, index) => {
              const itemUrl = itemUrls[index]
              return flattenItemAssets({ features: [item] }, itemUrl)
            })
          }

          state.itemsByDatasetId[dataset.id] = assets
          renderItemsModal(dataset, assets)
          renderDetails()
        } catch (error) {
          renderItemsModal(dataset, [], `Unable to load items for this dataset: ${error.message}`)
        }
      }

      function extractServiceType(collection) {
        return collection.service_type || collection['pw:service_type'] || collection.assets?.erddap?.['pw:service_type'] || 'unknown'
      }

      function extractBbox(collection) {
        const bbox = collection?.extent?.spatial?.bbox?.[0]
        if (!Array.isArray(bbox) || bbox.length < 4) return null
        const values = bbox.slice(0, 4).map(Number)
        if (values.some(Number.isNaN)) return null
        return values
      }

      function extractDateRange(collection) {
        const directStart = collection?.time_coverage_start
        const directEnd = collection?.time_coverage_end
        const extraStart = collection?.extra_fields?.time_coverage_start
        const extraEnd = collection?.extra_fields?.time_coverage_end

        const start = directStart || extraStart || null
        const end = directEnd || extraEnd || null

        if (start || end) {
          return `${start || 'start unknown'} to ${end || 'end unknown'}`
        }

        const interval = collection?.extent?.temporal?.interval?.[0]
        if (!Array.isArray(interval) || interval.length < 2) {
          return 'n/a'
        }

        const intervalStart = interval[0] || 'start unknown'
        const intervalEnd = interval[1] || 'end unknown'
        return `${intervalStart} to ${intervalEnd}`
      }

      function extractDataAccessForm(collection) {
        const links = collection.links || []
        const serviceLink = links.find(
          (link) => link.rel === 'service' && typeof link.href === 'string' && link.href.length > 0,
        )
        return serviceLink?.href || ''
      }

      function extractDataAccessExternal(collection) {
        const links = collection.links || []
        const serviceLink = links.find(
          (link) => link.rel === 'service' && typeof link.href === 'string' && link.href.length > 0,
        )
        return serviceLink?.external === true
      }

      function extractAssetsFilesAsset(collection) {
        const fromAssetsObject = collection?.assets?.files
        if (fromAssetsObject && typeof fromAssetsObject === 'object') {
          return fromAssetsObject
        }

        const fromColonField = collection?.['assets:files']
        if (fromColonField && typeof fromColonField === 'object') {
          return fromColonField
        }

        const fromDataAsset = collection?.assets?.data
        if (fromDataAsset && typeof fromDataAsset === 'object') {
          return fromDataAsset
        }

        const assets = Object.values(collection?.assets || {})
        const roleBasedDataAsset = assets.find((asset) => {
          if (!asset || typeof asset !== 'object') return false
          if (typeof asset.href !== 'string' || asset.href.length === 0) return false
          const roles = Array.isArray(asset.roles) ? asset.roles : []
          return roles.includes('data')
        })
        if (roleBasedDataAsset) {
          return roleBasedDataAsset
        }

        return null
      }

      function extractErddapDataFormLink(collection) {
        const links = collection?.links || []
        const erddapLink = links.find(
          (link) => ['erddap', 'erddap_endpoint'].includes(link.rel) && typeof link.href === 'string' && link.href.length > 0,
        )
        return erddapLink?.href || ''
      }

      function extractAssetDataHref(collection) {
        const href = collection?.assets?.data?.href
        return typeof href === 'string' && href.length > 0 ? href : ''
      }

      function extractHttpsDataFilesLink(collection) {
        const filesAsset = extractAssetsFilesAsset(collection)
        if (typeof filesAsset?.href === 'string' && filesAsset.href.length > 0) {
          return filesAsset.href
        }

        return ''
      }

      function extractHttpsDataFilesExternal(collection) {
        const filesAsset = extractAssetsFilesAsset(collection)
        return filesAsset?.external === true
      }

      function extractPrimaryDataAssetHref(collection) {
        const assets = Object.values(collection?.assets || {})

        const dataAsset = assets.find((asset) => {
          if (typeof asset?.href !== 'string' || asset.href.length === 0) {
            return false
          }

          const roles = Array.isArray(asset.roles) ? asset.roles : []
          const type = `${asset.type || ''}`.toLowerCase()
          const title = `${asset.title || ''}`.toLowerCase()

          return roles.includes('data') || type.includes('netcdf') || type.includes('hdf') || title.includes('data')
        })

        if (dataAsset?.href) {
          return dataAsset.href
        }

        return assets.find((asset) => typeof asset?.href === 'string' && asset.href.length > 0)?.href || ''
      }

      function extractDatasetInformation(collection) {
        const info = (collection.links || []).find(
          (link) => link.rel === 'describedby' && typeof link.href === 'string' && (/\/info\//.test(link.href) || /dataset information/i.test(link.title || '')),
        )
        if (info) return info.href
        const metadataAsset = Object.values(collection.assets || {}).find((asset) => typeof asset?.href === 'string' && /\/info\//.test(asset.href))
        return metadataAsset?.href || ''
      }

      function extractProjEpsg(collection) {
        if (collection?.['proj:epsg'] !== undefined && collection?.['proj:epsg'] !== null) {
          return String(collection['proj:epsg'])
        }

        const summaryValue = collection?.summaries?.['proj:epsg']
        if (Array.isArray(summaryValue) && summaryValue.length > 0) {
          return String(summaryValue[0])
        }

        return 'n/a'
      }

      function extractProjProj4(collection) {
        if (typeof collection?.['proj:proj4'] === 'string' && collection['proj:proj4'].length > 0) {
          return collection['proj:proj4']
        }

        return 'n/a'
      }

      function extractCreatorName(collection) {
        return collection?.creator_name || collection?.['pw:creator_name'] || collection?.extra_fields?.creator_name || 'n/a'
      }

      function extractAllLinks(collection) {
        const links = collection.links || []

        const findRel = (relName) => {
          const found = links.find((link) => link.rel === relName && typeof link.href === 'string' && link.href.length > 0)
          return found ? { title: found.title || relName, href: found.href, type: found.type || '' } : null
        }

        const describedby = links
          .filter((link) => link.rel === 'describedby' && typeof link.href === 'string' && link.href.length > 0)
          .map((link) => ({
            title: link.title || 'describedby',
            href: link.href,
            type: link.type || '',
          }))

        const assets = Object.entries(collection.assets || {})
          .filter(([, asset]) => typeof asset?.href === 'string' && asset.href.length > 0)
          .map(([key, asset]) => ({
            key,
            title: asset.title || key,
            href: asset.href,
            type: asset.type || '',
          }))

        return {
          self: findRel('self'),
          root: findRel('root'),
          parent: findRel('parent'),
          about: findRel('about'),
          describedby,
          assets,
        }
      }

      function renderList() {
        datasetList.innerHTML = ''
        datasetCount.textContent = String(state.filtered.length)

        if (state.filtered.length === 0) {
          datasetList.innerHTML = '<p class="empty">No matching datasets.</p>'
          return
        }

        state.filtered.forEach((item) => {
          const button = document.createElement('button')
          button.className = `dataset-item${item.id === state.selectedId ? ' active' : ''}`
          button.innerHTML = `<div class="dataset-title">${item.title}</div><div class="dataset-id">${item.id}</div>`
          button.addEventListener('click', () => {
            state.selectedId = item.id
            renderList()
            renderDetails()
          })
          datasetList.appendChild(button)
        })
      }

      function renderDetails() {
        const selected = state.datasets.find((item) => item.id === state.selectedId)
        if (!selected) {
          detailsPanel.innerHTML = '<p class="empty">Select a dataset to view details.</p>'
          return
        }

        const providers = (selected.providers || [])
          .map((provider) => {
            if (isExternalLink(provider.url)) {
              return `<a href="${provider.url}" target="_blank" rel="noreferrer">${provider.name || 'Unknown provider'}</a>`
            }
            return provider.name || 'Unknown provider'
          })
          .join(', ')

        const oneLink = (label, linkObj) => {
          if (!linkObj?.href) {
            return `<p><strong>${label}:</strong> n/a</p>`
          }
          const linkLabel = `${linkObj.title}${linkObj.type ? ` (${linkObj.type})` : ''}`
          const click = isExternalLink(linkObj.href)
            ? `<a href="${linkObj.href}" target="_blank" rel="noreferrer">${linkLabel}</a>`
            : `<span>${linkLabel}</span>`
          return `<p><strong>${label}:</strong> ${click}<span class="dataset-id">${linkObj.href}</span></p>`
        }

        const describedByMarkup = (selected.allLinks?.describedby || []).length
          ? `<ul class="mb-2">${selected.allLinks.describedby
              .map((item) => {
                const label = `${item.title}${item.type ? ` (${item.type})` : ''}`
                const click = isExternalLink(item.href)
                  ? `<a href="${item.href}" target="_blank" rel="noreferrer">${label}</a>`
                  : `<span>${label}</span>`
                return `<li>${click}<div class="dataset-id">${item.href}</div></li>`
              })
              .join('')}</ul>`
          : '<p>n/a</p>'

        const assetsMarkup = (selected.allLinks?.assets || []).length
          ? `<ul class="mb-0">${selected.allLinks.assets
              .map((item) => {
                const label = `${item.key}: ${item.title}`
                const click = isOpenableLink(item.href)
                  ? `<a href="${item.href}" target="_blank" rel="noreferrer">${label}</a>`
                  : `<span>${label}</span>`
                return `<li>${click}<div class="dataset-id">${item.href}</div></li>`
              })
              .join('')}</ul>`
          : '<p>n/a</p>'

        const httpsDatafileMarkup = renderOpenLinkMarkup(selected.httpsDataFilesLink, selected.httpsDataFilesExternal)
        const dataAccessMarkup = renderOpenLinkMarkup(selected.dataAccessForm, selected.dataAccessExternal)
        const isErddapService = `${selected.serviceType || ''}`.toLowerCase() === 'erddap'
        const hasItemSources = selected.itemsLink || (Array.isArray(selected.itemLinks) && selected.itemLinks.length > 0)
        const dataAccessControlMarkup = isErddapService
          ? dataAccessMarkup
          : hasItemSources
            ? '<button id="openItemsBtn" class="btn btn-outline-primary btn-sm ms-2">Open Data File Downloads</button>'
            : dataAccessMarkup

        detailsPanel.innerHTML = `
          <div class="panel-header"><h3 class="mb-0">${selected.title}</h3></div>
          <p class="dataset-id-line">
            <span class="dataset-id"><strong>Dataset ID:</strong> ${selected.id}</span>
            <span class="service-tag">service_type: ${selected.serviceType || 'unknown'}</span>
          </p>
          <p><strong>Summary:</strong> ${selected.summary || 'No summary provided.'}</p>

          <p><strong>Creator:</strong> ${selected.creatorName || 'n/a'}</p>
          <p><strong>Providers:</strong> ${providers || 'n/a'}</p>
          <p><strong>Date Range:</strong> ${selected.dateRange || 'n/a'}</p>
          <p><strong>Region (W,S,E,N):</strong> ${selected.bbox ? selected.bbox.join(', ') : 'n/a'}</p>
          <p><strong>proj:epsg:</strong> ${selected.projEpsg || 'n/a'}</p>
          <p><strong>proj:proj4:</strong> ${selected.projProj4 || 'n/a'}</p>

          <p><strong>Data Files:</strong> ${httpsDatafileMarkup}</p>

          <p>
            <strong>Data Access:</strong>
            ${dataAccessControlMarkup}
            ${!isErddapService && hasItemSources && state.itemsByDatasetId[selected.id] ? `<span class="items-summary ms-2">${state.itemsByDatasetId[selected.id].length} assets, ${state.itemsByDatasetId[selected.id].filter((asset) => asset.isNetcdf).length} netCDF</span>` : ''}
          </p>


          <p>
            <strong>Dataset Metadata:</strong>
            <button id="openMetadataBtn" class="btn btn-outline-primary btn-sm ms-2">View Metadata</button>
            ${isExternalLink(selected.datasetInformation) ? `<a class="ms-2" href="${selected.datasetInformation}" target="_blank" rel="noreferrer">
              ERDDAP Info page</a>` : ''}
          </p>


          ${selected.loadError ? `<p class="error">Some details were unavailable: ${selected.loadError}</p>` : ''}
        `
        const openItemsBtn = document.getElementById('openItemsBtn')
        if (openItemsBtn) {
          openItemsBtn.addEventListener('click', () => {
            openItemsModal(selected)
          })
        }

        const openMetadataBtn = document.getElementById('openMetadataBtn')
        if (openMetadataBtn) {
          openMetadataBtn.addEventListener('click', () => {
            openMetadataModal(selected)
          })
        }
      }

      function applySearch() {
        const query = searchInput.value.trim().toLowerCase()
        const terms = query
          .split(/[\s,]+/)
          .map((term) => term.trim())
          .filter((term) => term.length > 0)

        if (terms.length === 0) {
          state.filtered = [...state.datasets]
        } else {
          state.filtered = state.datasets.filter((dataset) => {
            const keywords = Array.isArray(dataset.keywords) ? dataset.keywords.join(' ') : ''
            const providers = Array.isArray(dataset.providers) ? dataset.providers.map((provider) => provider?.name || '').join(' ') : ''
            const allLinks = Array.isArray(dataset.allLinks)
              ? dataset.allLinks
                  .map((link) => `${link?.label || ''} ${link?.href || ''} ${link?.rel || ''}`)
                  .join(' ')
              : ''
            const haystack = `${dataset.id} ${dataset.title || ''} ${dataset.summary || ''} ${keywords} ${providers} ${dataset.serviceType || ''} ${dataset.dateRange || ''} ${allLinks}`.toLowerCase()
            return terms.every((term) => haystack.includes(term))
          })
        }

        if (!state.filtered.some((item) => item.id === state.selectedId)) {
          state.selectedId = state.filtered[0]?.id || null
        }

        renderList()
        renderDetails()
      }

      async function loadCatalog() {
        setStatus('Loading catalog...')
        reloadBtn.disabled = true

        try {
          const catalog = await fetchJson(catalogUrl)
          catalogTitle.textContent = catalog.title || 'PolarWatch Data Catalog'

          const childLinks = (catalog.links || []).filter(
            (link) => link.rel === 'child' && typeof link.href === 'string' && /collections\/[^/]+\/collection\.json$/.test(link.href),
          )

          // return data from ERDDAP metadata
          const datasets = await Promise.all(
            childLinks.map(async (link) => {
              const id = (link.href.match(/collections\/([^/]+)\/collection\.json$/) || [])[1]
              if (!id) return null

              try {
                const collection = await fetchJson(`stac/collections/${encodeURIComponent(id)}/collection.json`)
                return {
                  id,
                  title: collection.title || link.title || id,
                  collectionUrl: `stac/collections/${encodeURIComponent(id)}/collection.json`,
                  summary: collection.description || '',
                  dateRange: extractDateRange(collection),
                  serviceType: extractServiceType(collection),
                  projEpsg: extractProjEpsg(collection),
                  projProj4: extractProjProj4(collection),
                  creatorName: extractCreatorName(collection),
                  bbox: extractBbox(collection),
                  providers: collection.providers || [],
                  dataAccessForm: extractDataAccessForm(collection),
                  dataAccessExternal: extractDataAccessExternal(collection),
                  erddapDirectoryLink: extractErddapDataFormLink(collection),
                  httpsDataFilesLink: extractHttpsDataFilesLink(collection),
                  httpsDataFilesExternal: extractHttpsDataFilesExternal(collection),
                  datasetInformation: extractDatasetInformation(collection),
                  itemsLink: extractItemsLink(collection),
                  itemLinks: extractItemLinks(collection),
                  allLinks: extractAllLinks(collection),
                  keywords: collection.keywords || [],
                }
              } catch (error) {
                return {
                  id,
                  title: link.title || id,
                  collectionUrl: `stac/collections/${encodeURIComponent(id)}/collection.json`,
                  summary: '',
                  dateRange: 'n/a',
                  serviceType: '',
                  projEpsg: 'n/a',
                  projProj4: 'n/a',
                  creatorName: 'n/a',
                  bbox: null,
                  providers: [],
                  dataAccessForm: '',
                  dataAccessExternal: false,
                  erddapDirectoryLink: '',
                  httpsDataFilesLink: '',
                  httpsDataFilesExternal: false,
                  datasetInformation: '',
                  itemsLink: '',
                  itemLinks: [],
                  allLinks: [],
                  keywords: [],
                  loadError: error.message,
                }
              }
            }),
          )

          state.datasets = datasets.filter(Boolean).sort((a, b) => a.title.localeCompare(b.title))
          state.filtered = [...state.datasets]
          state.selectedId = state.filtered[0]?.id || null

          setStatus(state.datasets.length > 0 ? `  Loaded ${state.datasets.length} datasets` : 'No datasets found in catalog')
          renderList()
          renderDetails()
        } catch (error) {
          setStatus(`Catalog load failed: ${error.message}`)
          state.datasets = []
          state.filtered = []
          state.selectedId = null
          renderList()
          renderDetails()
        } finally {
          reloadBtn.disabled = false
        }
      }

      searchInput.addEventListener('input', applySearch)
      searchInput.addEventListener('keyup', applySearch)
      searchInput.addEventListener('change', applySearch)
      searchInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          event.preventDefault()
          applySearch()
        }
      })
  
      reloadBtn.addEventListener('click', loadCatalog)
      toggleDatasetsBtn.addEventListener('click', () => {
        state.datasetPanelHidden = !state.datasetPanelHidden
        applyDatasetPanelVisibility()
      })

      applyDatasetPanelVisibility()
      loadCatalog()
