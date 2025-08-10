# Moodico API 명세서

## 개요

Moodico는 색상 분석을 통한 화장품 추천 서비스입니다. 이 문서는 프로젝트의 모든 API 엔드포인트에 대한 상세한 명세를 제공합니다.

## 기본 정보

- **Base URL**: `http://localhost:8000/`
- **인증 방식**: Django 세션 기반 인증 + 카카오 OAuth
- **데이터 형식**: JSON
- **CSRF 보호**: 대부분의 API에서 활성화 (일부 API는 `@csrf_exempt` 적용)

---

## 1. 메인 페이지 API

### 1.1 메인 페이지 조회

- **URL**: `/`
- **Method**: `GET`
- **설명**: 메인 페이지 렌더링
- **응답**: HTML 페이지 (색상 매트릭스, 상위 좋아요 제품 포함)

---

## 2. 제품 관련 API

### 2.1 제품 상세 조회

- **URL**: `/products/<int:product_id>/`
- **Method**: `GET`
- **설명**: 특정 제품의 상세 정보 조회
- **응답**: HTML 페이지

### 2.2 제품 목록 조회

- **URL**: `/products/` 또는 `/products/products_list/`
- **Method**: `GET`
- **설명**: 전체 제품 목록 조회
- **응답**: HTML 페이지

### 2.3 제품 검색

- **URL**: `/products/search_product/`
- **Method**: `GET`
- **Query Parameters**:
  - `q` (string): 검색어
- **설명**: 제품명 또는 브랜드로 제품 검색
- **응답**:

```json
{
  "results": [
    {
      "id": "string",
      "name": "string",
      "brand": "string",
      "price": "string",
      "image": "string",
      "hex": "string"
    }
  ]
}
```

---

## 3. 좋아요 시스템 API

### 3.1 제품 좋아요 토글

- **URL**: `/products/toggle_product_like/`
- **Method**: `POST`
- **설명**: 제품 좋아요 추가/제거
- **Request Body**:

```json
{
  "product_id": "string",
  "product_name": "string",
  "product_brand": "string",
  "product_price": "string",
  "product_image": "string (optional)"
}
```

- **응답**:

```json
{
  "success": true,
  "is_liked": boolean,
  "message": "string"
}
```

- **에러 응답**:
  - `400`: 필수 정보 누락
  - `401`: 로그인 필요
  - `500`: 서버 오류

### 3.2 사용자 좋아요 목록 조회

- **URL**: `/products/get_user_likes/`
- **Method**: `GET`
- **설명**: 현재 로그인한 사용자의 좋아요 목록 조회
- **인증**: 로그인 필요
- **응답**:

```json
{
  "success": true,
  "likes": [
    {
      "product_id": "string",
      "product_name": "string",
      "product_brand": "string",
      "product_price": "string",
      "product_image": "string",
      "created_at": "datetime"
    }
  ]
}
```

### 3.3 제품별 좋아요 개수 조회

- **URL**: `/products/like_count/`
- **Method**: `GET`
- **Query Parameters**:
  - `product_id` (string): 제품 ID
- **설명**: 특정 제품의 총 좋아요 개수와 현재 사용자의 좋아요 상태 조회
- **응답**:

```json
{
  "success": true,
  "like_count": integer,
  "is_liked": boolean
}
```

### 3.4 여러 제품 좋아요 정보 일괄 조회

- **URL**: `/products/multiple_like_info/`
- **Method**: `GET`
- **Query Parameters**:
  - `product_ids[]` (array): 제품 ID 배열
- **설명**: 여러 제품의 좋아요 정보를 한 번에 조회
- **응답**:

```json
{
  "success": true,
  "products": {
    "product_id_1": {
      "like_count": integer,
      "is_liked": boolean
    },
    "product_id_2": {
      "like_count": integer,
      "is_liked": boolean
    }
  }
}
```

### 3.5 찜한 제품 페이지

- **URL**: `/products/liked_products/`
- **Method**: `GET`
- **설명**: 사용자가 좋아요한 제품들의 목록과 색상 매트릭스 표시
- **인증**: 로그인 필요
- **응답**: HTML 페이지 (제품 목록 + 색상 매트릭스)

---

## 4. 제품 랭킹 API

### 4.1 제품 랭킹 API

- **URL**: `/products/ranking/api/`
- **Method**: `GET`
- **Query Parameters**:
  - `limit` (integer, optional): 조회할 제품 수 (기본값: 10)
- **설명**: 전체 사용자의 좋아요를 기반으로 한 제품 랭킹 조회
- **응답**:

```json
{
  "success": true,
  "products": [
    {
      "product_id": "string",
      "product_name": "string",
      "product_brand": "string",
      "product_price": "string",
      "product_image": "string",
      "like_count": integer
    }
  ]
}
```

### 4.2 제품 랭킹 페이지

- **URL**: `/products/ranking/`
- **Method**: `GET`
- **설명**: 상위 10개 제품의 랭킹 페이지
- **응답**: HTML 페이지

---

## 5. 색상 매트릭스 API

### 5.1 색상 매트릭스 탐색

- **URL**: `/products/color_matrix_explore/`
- **Method**: `GET`
- **설명**: 색상 매트릭스 페이지 (모든 제품 표시)
- **응답**: HTML 페이지

---

## 6. 이미지 업로드 및 색상 분석 API

### 6.1 색상 이미지 업로드

- **URL**: `/upload/upload_color_image/`
- **Method**: `POST`
- **설명**: 이미지 업로드 및 색상 분석
- **Request**: multipart/form-data
- **응답**: HTML 페이지 (색상 분석 결과)

### 6.2 이미지 프록시

- **URL**: `/upload/proxy_image/`
- **Method**: `GET`
- **설명**: 외부 이미지 URL을 통한 이미지 프록시
- **응답**: 이미지 파일

---

## 7. 추천 시스템 API

### 7.1 내 아이템 기반 추천

- **URL**: `/recommend/my_item_recommendation/`
- **Method**: `GET`
- **설명**: 사용자가 소유한 아이템을 기반으로 한 제품 추천
- **응답**: HTML 페이지

### 7.2 색상 기반 추천

- **URL**: `/recommend/recommend_by_color/`
- **Method**: `GET`
- **설명**: 특정 색상을 기반으로 한 제품 추천
- **응답**: HTML 페이지

---

## 8. 무드 테스트 API

### 8.1 무드 테스트 페이지

- **URL**: `/moodtest/`
- **Method**: `GET`
- **설명**: 무드 테스트 질문 페이지
- **응답**: HTML 페이지

### 8.2 무드 테스트 결과

- **URL**: `/moodtest/mood_result/`
- **Method**: `GET`
- **설명**: 무드 테스트 결과 및 추천 제품 표시
- **응답**: HTML 페이지

---

## 9. 사용자 인증 API

### 9.1 회원가입

- **URL**: `/users/signup/`
- **Method**: `GET/POST`
- **설명**: 사용자 회원가입
- **응답**: HTML 페이지

### 9.2 로그인

- **URL**: `/users/login/`
- **Method**: `GET/POST`
- **설명**: 사용자 로그인
- **응답**: HTML 페이지

### 9.3 로그아웃

- **URL**: `/users/logout/`
- **Method**: `GET`
- **설명**: 사용자 로그아웃
- **응답**: 로그인 페이지로 리다이렉트

### 9.4 카카오 OAuth 인증

- **URL**: `/users/authorize/`
- **Method**: `GET`
- **설명**: 카카오 로그인 인증 시작
- **응답**: 카카오 인증 페이지로 리다이렉트

### 9.5 카카오 OAuth 콜백

- **URL**: `/users/kakao/callback/`
- **Method**: `GET`
- **설명**: 카카오 인증 후 콜백 처리
- **응답**: 메인 페이지로 리다이렉트

### 9.6 카카오 로그아웃

- **URL**: `/users/kakao_logout/`
- **Method**: `GET`
- **설명**: 카카오 계정 로그아웃
- **응답**: 로그인 페이지로 리다이렉트

### 9.7 사용자 프로필

- **URL**: `/users/profile/`
- **Method**: `GET`
- **설명**: 사용자 프로필 정보 조회
- **인증**: 로그인 필요
- **응답**: HTML 페이지

---

## 10. 관리자 API

### 10.1 좋아요 전체 삭제

- **URL**: `/products/clear_likes/`
- **Method**: `POST`
- **설명**: 모든 사용자의 좋아요 데이터 삭제 (관리자 전용)
- **인증**: 관리자 권한 필요
- **응답**:

```json
{
  "success": true
}
```

---

## 11. 데이터 모델

### 11.1 ProductLike 모델

```python
class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_nickname = models.CharField(max_length=100, null=True, blank=True)
    product_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    product_brand = models.CharField(max_length=255)
    product_price = models.CharField(max_length=100)
    product_image = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product_id']
```

---

## 12. 에러 처리

### 12.1 공통 에러 응답 형식

```json
{
  "success": false,
  "message": "에러 메시지"
}
```

### 12.2 HTTP 상태 코드

- `200`: 성공
- `400`: 잘못된 요청 (필수 파라미터 누락, 잘못된 데이터 형식)
- `401`: 인증 필요
- `403`: 권한 없음
- `404`: 리소스 없음
- `500`: 서버 내부 오류

---

## 13. 보안 고려사항

### 13.1 CSRF 보호

- 대부분의 POST 요청에 CSRF 토큰 필요
- 일부 API는 `@csrf_exempt` 데코레이터로 보호 해제

### 13.2 인증 및 권한

- 좋아요 관련 API: 로그인 또는 세션 기반 인증
- 관리자 API: Django 관리자 권한 필요
- 카카오 OAuth: OAuth 2.0 표준 준수

### 13.3 데이터 검증

- 모든 입력 데이터에 대한 검증 로직 구현
- SQL 인젝션 방지를 위한 Django ORM 사용
- XSS 방지를 위한 템플릿 이스케이핑

---

## 14. 성능 최적화

### 14.1 데이터베이스 최적화

- 좋아요 개수 집계를 위한 인덱스 활용
- N+1 쿼리 문제 방지를 위한 `select_related` 사용

### 14.2 캐싱 전략

- 클라이언트 사이드 캐싱 (좋아요 상태)
- 정적 데이터 (제품 정보) JSON 파일 활용

---

## 15. 개발 환경 설정

### 15.1 필수 패키지

```
Django>=4.0
numpy
requests
Pillow
```

### 15.2 환경 변수

```
DEBUG=True
SECRET_KEY=your_secret_key
KAKAO_CLIENT_ID=your_kakao_client_id
```

---

## 16. 테스트

### 16.1 API 테스트 방법

```bash
# Django 서버 실행
python manage.py runserver

# API 테스트 (예시)
curl -X GET http://localhost:8000/products/ranking/api/
curl -X POST http://localhost:8000/products/toggle_product_like/ \
  -H "Content-Type: application/json" \
  -d '{"product_id":"test","product_name":"Test Product","product_brand":"Test Brand","product_price":"10000"}'
```

---

## 17. 변경 이력

### v1.0.0 (2024-01-XX)

- 초기 API 구현
- 좋아요 시스템 구현
- 색상 매트릭스 및 추천 시스템 구현
- 카카오 OAuth 인증 구현
- 제품 랭킹 시스템 구현

---

## 18. 문의 및 지원

- **개발자**: Moodico 개발팀
- **문의**: [이메일 또는 연락처]
- **문서 버전**: 1.0.0
- **최종 업데이트**: 2024년 1월
